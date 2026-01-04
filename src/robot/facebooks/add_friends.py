# src/robot/facebooks/takecare.py
import re
from typing import Dict, Any, Tuple, List
from playwright.sync_api import Page, Locator

from src.my_types import Statuses
from src.utils.logger import Logger
from playwright._impl._errors import (
    TargetClosedError,
    TimeoutError,
)

class XpathSelectors:
    @staticmethod
    def xpath2_to_xpath1(xpath: str) -> str:
        """
        Converts XPath 2.0 specific functions (lower-case, exists) to XPath 1.0.
        """
        upper = "'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"
        lower = "'abcdefghijklmnopqrstuvwxyz'"
        new_xpath = xpath
        lower_case_pattern = r"lower-case\(\s*([^()]+(?:\([^()]*\)[^()]*)*)\s*\)"
        lower_case_repl = f"translate(\\1, {upper}, {lower})"
        
        while "lower-case(" in new_xpath:
            temp = re.sub(lower_case_pattern, lower_case_repl, new_xpath)
            if temp == new_xpath:
                break
            new_xpath = temp
        exists_pattern = r"exists\(\s*([^()]+(?:\([^()]*\)[^()]*)*)\s*\)"
        exists_repl = r"\1"
        
        while "exists(" in new_xpath:
            temp = re.sub(exists_pattern, exists_repl, new_xpath)
            if temp == new_xpath:
                break
            new_xpath = temp
                
        return new_xpath
    add_friend = xpath2_to_xpath1("//div[@role='button' and contains(lower-case(@aria-label), 'add friend') and (not(@aria-disabled) or @aria-disabled='false')]")
    confirm_request = xpath2_to_xpath1("//div[@role='button' and contains(lower-case(@aria-label), 'confirm request') and (not(@aria-disabled) or @aria-disabled='false')]")
    
def add_friends(page: Page, action_payload: Dict[str, Any]):
    # https://www.facebook.com/profile.php?id={uid}
    list_uid = action_payload.get("list_uid", [])
    friend_count = action_payload.get("friend_count", 3)
    count = 0
    for uid in list_uid:
        if count >= friend_count:
            break
        url = f"https://www.facebook.com/profile.php?id={uid}"
        __goto(page, url)
        if __add_friend(page):
            count += 1
        else: continue
    return True, Statuses.playwright_finished

def __goto(page: Page, url: str):
    try:
        page.goto(url, timeout=60_000)
        return True, Statuses.playwright__redirected
    except TargetClosedError as e:
        return False, Statuses.playwright__targetClosed
    except Exception as e:
        if "net::ERR_ABORTED" in str(e):
            return False, Statuses.playwright__aborted
        elif "net::ERR_TIMED_OUT" in str(e):
            return False, Statuses.playwright__retry
        elif "Page.set_content" in str(e):
            return False, Statuses.playwright__retry
        elif "net::ERR_EMPTY_RESPONSE" in str(e):
            return False, Statuses.playwright__retry
        elif "net::ERR_PROXY_CONNECTION_FAILED" in str(e):
            return False, Statuses.playwright__retry
        elif "net::ERR_CONNECTION_CLOSED" in str(e):
            return False, Statuses.playwright__retry
        elif "Page.goto" in str(e):
            return False, Statuses.playwright__retry
        else:
            return False, str(e)

def __add_friend(page: Page):
    page.wait_for_load_state("load")
    try:
        add_btn = page.locator(XpathSelectors.add_friend)
        if add_btn.count():
            add_btn.click()
            page.wait_for_timeout(3_000)
            return True
        else:
            confirm_btn = page.locator(XpathSelectors.confirm_request)
            confirm_btn.click()
            return False
    except:
        return False