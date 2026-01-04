# src/robot/facebooks/launch.py
from typing import Dict, Any, Tuple
from playwright.sync_api import Page
from playwright._impl._errors import (
    TargetClosedError
)
from src.my_types import Statuses
from src.utils.logger import Logger

def launch(page: Page, action_payload: Dict[str, Any]) -> Tuple[bool, str]:
    logger = Logger(__name__)
    try:
        page.goto(action_payload.get("url", "https://www.facebook.com"))
        page.wait_for_event(event="close", timeout=0)
        return True, Statuses.playwright_finished
    except TargetClosedError as e:
        return True, Statuses.playwright_finished
        return False, Statuses.playwright__targetClosed
    except Exception as e:
        if "net::ERR_ABORTED" in str(e):
            return True, Statuses.playwright__aborted
        elif "net::ERR_TIMED_OUT" in str(e):
            return False, Statuses.playwright__retry
        elif "Page.set_content" in str(e):
            return False, Statuses.playwright__retry
        elif "Page.goto" in str(e):
            return False, Statuses.playwright__retry
        else:
            logger.error(str(e))