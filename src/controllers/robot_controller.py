# src/controllers/robot_controller.py

from typing import Optional, Dict, Any, List
from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal

from src.services._service_manager import Service_Manager
from src.robot.check_fb_live import CheckLive
from src.robot.playwright_manager import PlaywrightManager
from src.utils.logger import Logger
from src.my_constants import ROBOT_ACTION_OPTIONS

class Robot_Controller(QObject):
    def __init__(self, service_manager: Service_Manager, parent=None):
        super().__init__(parent)
        self.logger = Logger(self.__class__.__name__)
        self.service_manager = service_manager
        self.check_live_manager:Optional[CheckLive] = None
        self.playwright_manager: Optional[PlaywrightManager] = None
    
    def handle_check_live(self, list_id_uids: List[str]):
        if not list_id_uids:
            return
        self.logger.info(f"Start check {len(list_id_uids)} facebook account.")
        if self.check_live_manager and not self.check_live_manager._check_if_done()[0]:
            self.check_live_manager.add_tasks(list_id_uids)
        else:
            self.check_live_manager = CheckLive()
            self.check_live_manager.task_succeeded.connect(
                self.__on_check_live_task_succeeded
            )
            self.check_live_manager.task_failed.connect(self.__on_check_live_task_failed)
            self.check_live_manager.all_tasks_finished.connect(
                self.__check_live_all_tasks_finished
            )

            self.check_live_manager.add_tasks(list_id_uids)
    
    @pyqtSlot(tuple, tuple, bool)
    def __on_check_live_task_succeeded(
        self, id_uid: tuple, task_per_all: tuple, is_live: bool
    ):
        self.logger.info(
            f"Check live ({task_per_all[0]}/{task_per_all[1]}) {id_uid[0]} ({id_uid[1]}) -> {is_live}"
        )
        if type(is_live) != bool:
            return
        self.service_manager.profile_service.change_status(
            id_uid[0], is_live
        )
    
    @pyqtSlot(tuple, str)
    def __on_check_live_task_failed(self, id_uid: tuple, error_message: str):
        self.logger.failed(f"{id_uid[0]} ({id_uid[1]}): {error_message}")

    @pyqtSlot()
    def __check_live_all_tasks_finished(self):
        self.logger.succeed("Check live finished")
    
    def handle_facebook_action(self, tasks: List[Dict[str, Any]], settings: Dict[str, Any]):
        if self.playwright_manager and not self.playwright_manager.is_all_task_finished():
            self.logger.info(
                "Bot is already running. Adding browser task to the queue."
            )
            self.playwright_manager.add_task(tasks, settings)
        else:
            self.logger.warning("Starting new bot tasks.")
            self.playwright_manager = PlaywrightManager(service_manager=self.service_manager)
            self.playwright_manager.add_task(tasks, settings)