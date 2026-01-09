# src/robot/robot_manager.py
import inspect, re
from typing import Dict, Any, List
from collections import deque
from PyQt6.QtCore import QThreadPool, QObject, pyqtSlot, QTimer, pyqtSignal
from PyQt6.QtGui import QGuiApplication

from src.utils.logger import Logger
from src.utils.cookies_handlers import write_cookies
from src.my_types import Playwright_Signals, PlaywrightSignal_Type, Profile_Type, Statuses
from src.my_constants import TAKE_CARE__ADD_FRIEND
from src.services._service_manager import Service_Manager
from src.robot.playwright_worker import PlaywrightWorker

SETTING_PROXY_OPTION = "proxy"
MOBILE_SIZE = (375, int(375 * 1.5))
DESKTOP_SIZE = (960, int(950 * 0.56))

class PlaywrightManager(QObject):
    def __init__(self, service_manager: Service_Manager, parent=None):
        super().__init__(parent)
        self.service_manager = service_manager

        self._settings: Dict[str, Any] = {}
        self._pending_tasks = deque()
        self._pending_proxies: deque[str] = deque()
        self._in_progress_tasks: Dict[str, Any] = {}
        self._total_task: int = 0
        self._max_thread: int = 8
        self.threadpool = QThreadPool.globalInstance()
        self.signals = Playwright_Signals()
        self._pending_pos = self.__init_browser_pos()
        self.logger = Logger(self.__class__.__name__)
    
    def add_task(self, tasks: List[Dict[str, Any]], settings: Dict[str, Any]):
        for task in tasks:
            self._pending_tasks.append(task)
            self._total_task += 1
        self._pending_proxies = self.__get_raw_proxies()
        self._settings = settings
        self.try_start_task()

    def try_start_task(self):
        available_thread = min(
            self._settings.get("thread_num", len(self._pending_proxies)),
            len(self._pending_proxies),
            self._max_thread,
        )
        while (
            self._pending_tasks
            and self.threadpool.activeThreadCount() < self._max_thread
            and len(self._in_progress_tasks) < self._max_thread
            and self._pending_proxies
            and available_thread
        ):
            task = self._pending_tasks.popleft()
            task_profile_payload: Dict[str, Any] = task.get("profile")
            task_aciton_payload: Dict[str, Any] = task.get("action_payload")
            if task_aciton_payload.get("action_name") == TAKE_CARE__ADD_FRIEND:
                task_aciton_payload["list_uid"] = self.service_manager.profile_service.get_all_uid()
            if not task_profile_payload:
                self.logger.error("missing profile")
                return
            profile_info:Profile_Type = task_profile_payload.get("info")
            raw_proxy = self._pending_proxies.popleft()
            browser_pos = self._pending_pos.popleft()
            available_thread -= 1
            worker_signals = Playwright_Signals()
            worker = PlaywrightWorker({
                "task": task,
                "raw_proxy": raw_proxy,
                "browser_position": browser_pos,
            }, worker_signals)

            self._in_progress_tasks[profile_info.id] = {
                "task": task,
                "proxy": raw_proxy,
                "browser_pos": browser_pos,
                "worker": worker,
                "signals": worker_signals,
            }
            worker_signals.info.connect(self.__on_worker_info)
            worker_signals.warning.connect(self.__on_worker_warning)
            worker_signals.error.connect(self.__on_worker_error)
            worker_signals.failed.connect(self.__on_worker_failed)
            worker_signals.finished.connect(self.__on_worker_finished)
            worker_signals.retry.connect(self.__on_worker_retry)
            worker_signals.cookies.connect(self.__on_worker_cookies)

            self.threadpool.start(worker)
        self.logger.info(f"Pending ({len(self._pending_tasks)}) - processing ({len(self._in_progress_tasks)})")

    def is_all_task_finished(self) -> bool:
        if len(self._pending_tasks) or len(self._in_progress_tasks):
            return False
        return True
    
    def __init_browser_pos(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width, screen_height = screen_geometry.width(), screen_geometry.height()

        browser_w, browser_h = DESKTOP_SIZE
        offset_x = int(browser_w * 0.3)
        offset_y = int(browser_h * 0.4)
        y_step_per_col = int(offset_y / 3)

        positions = []
        current_x, current_y, base_y_of_row = 0, 0, 0
        MAX_POSITIONS = 20

        while len(positions) < MAX_POSITIONS:
            if (current_x + browser_w) > screen_width:
                current_x = 0
                base_y_of_row += offset_y
                current_y = base_y_of_row
                if (base_y_of_row + browser_h) > screen_height:
                    break

            positions.append({"x": current_x, "y":current_y})
            current_x += offset_x
            current_y += y_step_per_col

        return deque(positions)

    def __get_raw_proxies(self):
        return deque(self.service_manager.setting_service.get_proxies_selected())

    @pyqtSlot(dict)
    def __on_worker_info(self, res: dict):
        payload = res.get("payload")
        status = res.get("status")
        message = res.get("message")

        task = payload.get("task")
        browser_position = payload.get("browser_position")
        raw_proxy = payload.get("raw_proxy") 
    @pyqtSlot(dict)
    def __on_worker_warning(self, res: dict): pass
    @pyqtSlot(dict)
    def __on_worker_error(self, res: dict): pass
    @pyqtSlot(dict)
    def __on_worker_failed(self, res: dict): pass
    
    @pyqtSlot(dict)
    def __on_worker_finished(self, res: dict):
        payload = res.get("payload")
        task = payload.get("task")
        task_profile_payload: Dict[str, Any] = task.get("profile")
        profile_info:Profile_Type = task_profile_payload.get("info")
        browser_position = payload.get("browser_position")
        raw_proxy = payload.get("raw_proxy")
        self.logger.info(f"{profile_info.id} - {profile_info.uid} - {profile_info.username}: Finished")
        self._pending_proxies.append(raw_proxy)
        self._pending_pos.append(browser_position)
        self.__clear_worker_and_signals(profile_info.id)
        if not self.is_all_task_finished():
            self.try_start_task()
        else:
            self.logger.succeed("All task finished!")
    
    @pyqtSlot(dict)
    def __on_worker_retry(self, res: dict):
        payload = res.get("payload")
        status = res.get("status")
        message = res.get("message")

        task = payload.get("task")
        browser_position = payload.get("browser_position")
        raw_proxy = payload.get("raw_proxy")
        
        task_profile_payload: Dict[str, Any] = task.get("profile")
        profile_info: Profile_Type = task_profile_payload.get("info")
        self.__clear_worker_and_signals(profile_info.id)
        
        self._pending_pos.append(browser_position)
        self._pending_tasks.append(task)

        msg = ""
        if message: msg = f"{status} - {message}"
        else: msg = status

        delay_ms = 10000
        if status == Statuses.proxy__recall:
            _ =  re.search(r'(\d+)s', message) #r'(\d+)s'
            second = int(_.group(1)) if int(_.group(1)) < 60 and int(_.group(1)) > 0 else 10
            delay_ms = int(second*1000)
        else:
            self.logger.debug(msg)
        warning_msg = f"Task for {profile_info.username} ({profile_info.uid}) recalled. Retrying in {float(delay_ms/ 1000)} seconds."
        self.logger.warning(warning_msg)

        def handle_delay():
            self._pending_proxies.append(raw_proxy)
            self.try_start_task()
              

        QTimer.singleShot(delay_ms, handle_delay)

    @pyqtSlot(str, str)
    def __on_worker_cookies(self, uid:str, cookies: str):
        is_write = write_cookies(uid, cookies)
        if is_write:self.logger.info(f"Successfully wrote cookies for {uid} to file.")
        else: self.logger.waning(f"Failed wrote cookies for {uid} to file.")

    def __clear_worker_and_signals(self, key: str):
        if key in self._in_progress_tasks:
            try:
                entry = self._in_progress_tasks.get(key) or {}
                signals_obj = entry.get("signals")
                self.__disconnect_all_signals(signals_obj)
            except Exception as e:
                print(e)
            try:
                self._in_progress_tasks.pop(key, None)
            except Exception:
                pass
    
    def __list_pyqt_signals(self, signals_object):
        signal_names = []
        for name, member in inspect.getmembers(signals_object):
            if isinstance(member, pyqtSignal): 
                signal_names.append(name)
        return signal_names

    def __disconnect_all_signals(self, signals_object):
        disconnected_count = 0
        signal_names = self.__list_pyqt_signals(signals_object)
        
        for name in signal_names:
            signal = getattr(signals_object, name)
            try:
                signal.disconnect()
                disconnected_count += 1
                print(f"✅ Disconnected all slots from signal: {name}")
            except TypeError as e:
                print(f"⚠️ Signal {name} was not connected or error during disconnect: {e}")
                pass
            
        return disconnected_count
    