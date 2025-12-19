# src/robot/facebooks/launch.py
from typing import Dict, Any, Tuple
from playwright.sync_api import Page, BrowserContext
from playwright._impl._errors import (
    TargetClosedError
)
from src.my_types import Statuses
from src.utils.logger import Logger

def get_cookies(context: BrowserContext, page: Page):
    logger =  Logger(__name__)
    try:
        page.goto("https://www.facebook.com")
        cookies_list = context.cookies()
        facebook_cookies = [cookie for cookie in cookies_list if ".facebook.com" in cookie.get("domain")]
        cookie_parts = []
        for cookie in facebook_cookies:
            cookie_parts.append(f"{cookie['name']}={cookie['value']}")
            
        cookie_string = "; ".join(cookie_parts)
        
        return True, cookie_string
        

    except TargetClosedError as e:
        return False, Statuses.playwright__targetClosed
    except Exception as e:
        if "net::ERR_ABORTED" in str(e):
            return True, Statuses.playwright__aborted
        elif "net::ERR_TIMED_OUT" in str(e):
            return False, Statuses.playwright__retry
        elif "Page.set_content" in str(e):
            return False, Statuses.playwright__retry
        else:
            logger.error(str(e))