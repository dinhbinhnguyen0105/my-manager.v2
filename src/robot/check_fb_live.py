import pycurl
import io
import json
from typing import List, Tuple, Dict
from collections import deque

from PyQt6.QtCore import QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    """
    Signals available from a running worker thread.
    success_signal: Emits (id, uid), is_live on successful check.
    error_signal: Emits (id, uid), error_message on failure.
    finished: Emits (id, uid) when the worker finishes (success or error).
    """

    success_signal = pyqtSignal(tuple, tuple, bool)
    error_signal = pyqtSignal(tuple, str)
    finished = pyqtSignal(tuple)


class CheckLiveWorker(QRunnable):
    """
    Worker to perform a single check for a UID using pycurl.
    """

    def __init__(self, id_uid: tuple, task_per_all):
        super().__init__()
        # id_uid is a tuple: (id_key, uid_string)
        self.id_uid = id_uid
        self.task_per_all = task_per_all
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        # Use the UID for the URL
        uid = self.id_uid[1]
        id_key = self.id_uid[0]
        url = f"https://graph.facebook.com/{uid}/picture?redirect=false"
        headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept: application/json",
            "Accept-Language: en-US,en;q=0.9",
            "Connection: keep-alive",
        ]

        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.CONNECTTIMEOUT, 10)
            curl.setopt(pycurl.TIMEOUT, 20)
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.setopt(pycurl.HTTPHEADER, headers)
            curl.perform()

            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            body = buffer.getvalue().decode("utf-8", errors="ignore")

            if status_code != 200:
                # Issue 1: Only emit error_signal on HTTP failure.
                error_msg = (
                    f"HTTP Error {status_code} for UID {uid}. Response: {body[:200]}..."
                )
                self.signals.error_signal.emit(self.id_uid, error_msg)
                # self.signals.success_signal.emit(self.id_uid, False) # REMOVED: Confusing logic
            else:
                try:
                    data = json.loads(body)
                    is_live = bool(data.get("data", {}).get("height", False))
                    self.signals.success_signal.emit(
                        self.id_uid, self.task_per_all, is_live
                    )
                except json.JSONDecodeError as e:
                    # Correctly uses UID in error message
                    error_msg = f"JSON Decode Error for UID {uid}: {e}. Response: {body[:200]}..."
                    self.signals.error_signal.emit(self.id_uid, error_msg)

        except pycurl.error as e:
            errno, errstr = e.args
            # Correctly uses UID in pycurl error message
            error_msg = f"PyCurl error {errno}: {errstr} for UID {uid}"
            self.signals.error_signal.emit(self.id_uid, error_msg)

        except Exception as e:
            # Correctly uses UID in general error message
            error_msg = f"Unexpected error for UID {uid}: {e}"
            self.signals.error_signal.emit(self.id_uid, error_msg)

        finally:
            curl.close()
            buffer.close()
            self.signals.finished.emit(self.id_uid)


class CheckLive(QObject):
    """
    Manages a queue of CheckLiveWorker tasks using a QThreadPool.
    """

    task_succeeded = pyqtSignal(tuple, tuple, bool)
    task_failed = pyqtSignal(tuple, str)
    all_tasks_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pending_tasks: deque[Tuple[str, str]] = deque()
        self._in_progress: Dict[str, Tuple[str, CheckLiveWorker]] = {}
        # Changed key type hint to str for consistency with _id
        self._succeeded: Dict[str, bool] = {}
        self._failed: Dict[str, str] = {}
        self._total_tasks = 0

        self.threadpool = QThreadPool.globalInstance()
        # Ensure max_workers does not exceed maxThreadCount
        max_workers = min(5, self.threadpool.maxThreadCount())
        self.threadpool.setMaxThreadCount(max_workers)

    @pyqtSlot(list)
    def add_tasks(self, tasks: List[Tuple[str, str]]):
        """
        Accepts list of (id, uid) tuples.
        """
        # Collect IDs currently pending or in progress
        seen_task = (
            set(id_key for id_key, uid in self._pending_tasks)
            | self._in_progress.keys()
        )

        for id_key, uid in tasks:
            if id_key not in seen_task:
                self._pending_tasks.append((id_key, uid))
                self._total_tasks += 1
                # Issue 2 FIX: Add only the ID key to seen_task
                seen_task.add(id_key)

        self._try_start_tasks()

    def _try_start_tasks(self):
        """
        Start queued tasks up to max concurrency.
        """
        available = (
            self.threadpool.maxThreadCount() - self.threadpool.activeThreadCount()
        )
        while available > 0 and self._pending_tasks:
            _id, uid = self._pending_tasks.popleft()
            worker = CheckLiveWorker(
                (_id, uid), (len(self._pending_tasks), self._total_tasks)
            )
            worker.signals.success_signal.connect(self._on_success)
            worker.signals.error_signal.connect(self._on_error)
            worker.signals.finished.connect(self._on_finished)

            self._in_progress[_id] = (uid, worker)
            self.threadpool.start(worker)
            available -= 1

    @pyqtSlot(tuple, tuple, bool)
    def _on_success(self, id_uid: tuple, task_per_all: tuple, is_live: bool):
        # Issue 3 FIX: Update internal results
        id_key = id_uid[0]
        self._succeeded[id_key] = is_live

        # Emit signal to main thread
        self.task_succeeded.emit(id_uid, task_per_all, is_live)

        # Try to start the next task
        self._try_start_tasks()

    def _check_if_done(self) -> Tuple[bool, int, int, int]:
        """
        Kiểm tra xem tất cả các tác vụ đã hoàn thành hay chưa và cung cấp số liệu thống kê.

        Trả về:
            tuple: (is_done, total_tasks, processed_count, remaining_tasks)
        """
        is_done = not self._pending_tasks and not self._in_progress
        processed_count = len(self._succeeded) + len(self._failed)
        remaining_tasks = len(self._pending_tasks) + len(self._in_progress)

        return is_done, self._total_tasks, processed_count, remaining_tasks

    @pyqtSlot(tuple, str)
    def _on_error(self, id_uid: tuple, error_msg: str):
        # Issue 3 FIX: Update internal results
        id_key = id_uid[0]
        self._failed[id_key] = error_msg

        # Emit signal to main thread
        self.task_failed.emit(id_uid, error_msg)

    @pyqtSlot(tuple)
    def _on_finished(self, id_uid: tuple):
        if id_uid[0] in self._in_progress:
            del self._in_progress[id_uid[0]]

        # Check if all tasks are complete
        if not self._pending_tasks and not self._in_progress:
            self.all_tasks_finished.emit()

        # Note: _try_start_tasks is not called here since success/error signals
        # (which are guaranteed to fire before finished) already handle starting
        # the next task.

    # _check_if_done() is unnecessary and has been removed based on logic review.

    def get_results(self) -> Dict[str, bool]:
        """Returns map of {id: is_live} for successful checks."""
        return self._succeeded

    def get_failed(self) -> Dict[str, str]:
        """Returns map of {id: error_message} for failed checks."""
        return self._failed
