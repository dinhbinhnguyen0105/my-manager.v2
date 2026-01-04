# src/controllers/robot_controller.py

from typing import Optional, Dict, Any, List
from PyQt6.QtCore import pyqtSlot, QObject, pyqtSignal

from src.services._service_manager import Service_Manager
from src.robot.check_fb_live import CheckLive
from src.robot.playwright_manager import PlaywrightManager
from src.utils.logger import Logger
from src.my_constants import (
    ROBOT_ACTION_OPTIONS,
    SELL__BY_MARKETPLACE,
    SELL__BY_GROUP,
    DISCUSSION__TO_GROUP,
    DISCUSSION__TO_NEW_FEED,
    SHARE__BY_MOBILE,
    SHARE__BY_DESKTOP,
    LAUNCH,
    TAKE_CARE__JOIN_GROUP,
    TAKE_CARE__ADD_FRIEND,
    TAKE_CARE__COMMENT_TO_GROUP,
    TAKE_CARE__COMMENT_TO_FRIEND_WALL,
    GET_COOKIES,
    PROFILE__NAME_OPTIONS,
)
from src.my_types import Profile_Type

class Robot_Controller(QObject):
    def __init__(self, service_manager: Service_Manager, parent=None):
        super().__init__(parent)
        self.logger = Logger(self.__class__.__name__)
        self.service_manager = service_manager
        self.check_live_manager: Optional[CheckLive] = None
        self.playwright_manager: Optional[PlaywrightManager] = None

    def init_robot_tasks(self, data):
        flattened_list = []
        for profile_id, content in data.items():
            profile_info = content['profile']
            actions = content['actions']
            
            for action in actions:
                flattened_list.append({
                    "profile": profile_info,
                    "action_payload": action
                })

        flattened_list.sort(key=lambda x: x['profile']['info'].username)

        from collections import defaultdict
        groups = defaultdict(list)
        for item in flattened_list:
            groups[item['profile']['info'].username].append(item)

        interleaved_list = []
        max_len = max(len(g) for g in groups.values())
        for i in range(max_len):
            for user in sorted(groups.keys()):
                if i < len(groups[user]):
                    interleaved_list.append(groups[user][i])

        return interleaved_list

    def init_action_payload(self, profile : Dict[str, Any], action: Dict[str, Any]):
        payload = {
            "profile": profile
        }
        if action.get("action_name") in [
            SELL__BY_MARKETPLACE,
            SELL__BY_GROUP,
            DISCUSSION__TO_GROUP,
            DISCUSSION__TO_NEW_FEED,
        ]:
            profile_info: Profile_Type = profile.get("info")
            if not hasattr(profile_info, Profile_Type):
                raise Exception("missing profile info")
            if not profile_info.status:
                return {}
            if profile_info.profile_name == list(PROFILE__NAME_OPTIONS.keys())[0]:
                service = self.service_manager.property_product_service
            else:
                service = self.service_manager.misc_product_service
            if "pid" in action.keys():
                if action["pid"] == "random":
                    service.get_random("sale", 7)
                    pass
                else:
                    service.read(action["pid"])
                    pass
            else:
                pass

            
        elif action.get("action_name") in [
            SHARE__BY_DESKTOP,
            LAUNCH,
            TAKE_CARE__JOIN_GROUP,
            TAKE_CARE__ADD_FRIEND,
            TAKE_CARE__COMMENT_TO_GROUP,
            TAKE_CARE__COMMENT_TO_FRIEND_WALL,
            GET_COOKIES,
        ]:
            payload["mobile_mode"] = False
            if action.get("action_name") == TAKE_CARE__ADD_FRIEND:
                payload["friend_list"] = self.service_manager.profile_service.get_all_uid()
        elif action.get("action_name") in [
            SHARE__BY_MOBILE,
        ]:
            payload["mobile_mode"] = True
        
        return payload

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
            self.check_live_manager.task_failed.connect(
                self.__on_check_live_task_failed)
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

    def handle_run_bot(self, tasks: List[Dict[str, Any]], settings: Dict[str, Any]):
        if self.playwright_manager and not self.playwright_manager.is_all_task_finished():
            self.logger.info(
                "Bot is already running. Adding browser task to the queue."
            )
            self.playwright_manager.add_task(tasks, settings)
        else:
            self.logger.warning("Starting new bot tasks.")
            self.playwright_manager = PlaywrightManager(
                service_manager=self.service_manager)
            self.playwright_manager.add_task(tasks, settings)
