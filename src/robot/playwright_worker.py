# src/robot/facebook_action_worker.py
from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import (
    sync_playwright
)
from undetected_playwright import Tarnished

from undetected_playwright import Tarnished
from PyQt6.QtCore import QRunnable

from src.my_exceptions import MyException
from src.my_constants import LAUNCH
from src.my_types import Playwright_Signals, Profile_Type, Statuses
from src.utils.proxy_handler import get_proxy
from src.utils.logger import Logger
from src.robot.action_mapping import ACTION_MAPING

MOBILE_SIZE = (375, int(375 * 1.5))
DESKTOP_SIZE = (960, int(950 * 0.56))

class PlaywrightWorker(QRunnable):
    def __init__(self, payload: Dict[str, Any], signals: Playwright_Signals):
        super().__init__()
        self.logger = Logger(self.__class__.__name__)

        self.data = payload
        self.task = payload.get("task")
        self.browser_position = payload.get("browser_position")
        self.raw_proxy = payload.get("raw_proxy")
        self.signals = signals

        task_profile_payload: Dict[str, Any] = self.task.get("profile")
        self.profile_info: Profile_Type = task_profile_payload.get("info")
        self.profile_path = task_profile_payload.get("profile_path")
        self.action_payload: Dict = self.task.get("action_payload")
        self.action_name = self.action_payload.get("action_name", LAUNCH)

    def run(self):
        try:
            result, status_code  = self.handle_playwright()
            if result:
                self.signals.finished.emit({"payload": self.data})        
            else:
                self.signals.retry.emit({
                    "payload": self.data,
                    "status": status_code
                })
        except MyException as e:
            if e.status in [
                Statuses.playwright__retry,
                Statuses.proxy__recall,
            ]:
                self.signals.retry.emit({
                    "payload": self.data,
                    "status": e.status,
                    "message": e.message
                })
            else:
                raise e
        except Exception as e:
            if "net::ERR_PROXY_CONNECTION_FAILED" in str(e):
                self.signals.retry.emit({
                    "payload": self.data,
                    "status": "net::ERR_PROXY_CONNECTION_FAILED",
                })
            else:
                raise e
    def handle_playwright(self) -> Tuple[bool, str]:
        with sync_playwright() as p:
            header = self.__init_header()
            context = p.chromium.launch_persistent_context(**header)
            if context.pages:
                context.pages[0].set_content(self.__init_info_page())
            Tarnished.apply_stealth(context)
            auto_page = context.new_page()

            return ACTION_MAPING[self.action_name](
                auto_page,
                self.action_payload,
            )
    
    def __init_header(self):
        mobile_mode = self.action_payload.get("mobile_mode")
        width = MOBILE_SIZE[0] if mobile_mode else DESKTOP_SIZE[0]
        hight = MOBILE_SIZE[1] if mobile_mode else DESKTOP_SIZE[1]
        return dict(
            user_data_dir = self.profile_path,
            user_agent = self.profile_info.mobile_ua if mobile_mode else self.profile_info.desktop_ua,
            headless = False,
            is_mobile = mobile_mode,
            has_touch = mobile_mode,
            viewport = {"width": width, "height": hight},
            screen = {"width": width, "height": hight},
            args=[
                "--disable-blink-features=AutomationControlled",

            ],
            ignore_default_args=["--enable-automation"],
            proxy=self.__init_proxy(),
        )
    
    def __init_info_page(self):
        info_html = f"""
            <html>
                <head><title>{self.profile_info.username.replace("\n", "")}</title></head>
                <body>
                    <h2>Username: {self.profile_info.username.replace("\n", "")}</h2>
                    <ul>
                        <li>id: {self.profile_info.id}</li>
                        <li>uid: {self.profile_info.uid}</li>
                        <li>user_data_dir: {self.profile_path}</li>
                    </ul>
                    <h2>Actions</h2>
                    
                </body>
            </html>
        """
        return info_html
    
    def __init_proxy(self):
        status, result = get_proxy(self.raw_proxy)
        if not status:
            raise MyException("GET_PROXY_ERROR", Statuses.proxy__recall, result)
        return result
        