# src/robot/facebooks/join_groups.py
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
    
    feed = xpath2_to_xpath1('div[role="feed"]')
    article = xpath2_to_xpath1('//div[@role="article" and .//div[@role="button" and lower-case(normalize-space(.))="join"]]')
    group_name = xpath2_to_xpath1('//a[@role="presentation" and exists(@href)]')
    join_btn = xpath2_to_xpath1('//div[@role="button" and lower-case(normalize-space(.))="join" and not(@disabled) and not(@aria-hidden="true") and not(contains(@style, "display: none")) and not(contains(@style, "visibility: hidden"))]')
    loading_state = xpath2_to_xpath1('//div[lower-case(@aria-label)="loading..." and @role="status" and @data-visualcompletion="loading-state"]')

    dialog = xpath2_to_xpath1('//div[lower-case(@aria-label)="participant questions" and @role="dialog" and .//div[@role="button" and lower-case(@aria-label)="close"]]')
    close_btn = xpath2_to_xpath1('//div[@role="button" and lower-case(@aria-label)="close" and not(@disabled) and not(@aria-hidden="true") and not(contains(@style, "display: none")) and not(contains(@style, "visibility: hidden"))]')

def join_groups(page: Page, settings: Dict[str, Any]):
    is_redirected, status = __goto(page, settings.get("url", "https://www.facebook.com/search/groups/?q=bán nhà đà lạt"))
    if not is_redirected:
        return False, status
    groups = __get_groups(page)
    __join_groups(page, groups, 3)
    return True, Statuses.playwright_finished

def __goto(page: Page, url: str = "https://www.facebook.com/search/groups/?q=bán nhà đà lạt"):
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
        elif "Page.goto" in str(e):
            return False, Statuses.playwright__retry
        else:
            return False, str(e)

def __get_groups(page: Page) -> List[Dict[str, Any]]:
    groups = []
    
    try:
        feed = page.locator(XpathSelectors.feed)

        feed.first.wait_for()
    except:
        return []

    current_count = 0
    target_count = 100
    timeout = 30000 
    start_time = page.evaluate("Date.now()")

    while current_count < target_count:
        articles = feed.first.locator(XpathSelectors.article)
        new_count = articles.count()
        
        if new_count >= target_count:
            break
            
        if new_count > current_count:
            articles.last.scroll_into_view_if_needed()
            current_count = new_count
        else:
            articles.last.scroll_into_view_if_needed()
        try:
            page.wait_for_function(
                f"""() => document.querySelectorAll("{XpathSelectors.article.replace('//', '')}").length > {current_count}""",
                timeout=5000
            )
        except:
            if page.evaluate("Date.now()") - start_time > timeout:
                break
            continue
        loading = feed.first.locator(XpathSelectors.loading_state)
        if loading.count() < 1:
            break


    for article in articles.all():
        group_info = {
            "group_name": "",
            "group_url": "",
            "members": 0,
            "locator": None,
        }
        group_name = article.locator(XpathSelectors.group_name)
        group_info["group_name"] = group_name.text_content()
        group_info["group_url"] = group_name.get_attribute("href")
        group_info["members"] = __get_member_count(article.text_content())
        group_info["locator"] = article
        groups.append(group_info)
    return sorted(groups, key=lambda x: x["members"], reverse=True)

def __join_groups(page: Page, groups: List[Dict], num: int = 3):
    if not groups:
        return
    for group in groups[:num]:
        locator:Locator = group["locator"]
        try:
            locator.scroll_into_view_if_needed()
            __close_dialog(page)
            join_btn = locator.locator(XpathSelectors.join_btn)
            join_btn.first.click()
            page.wait_for_timeout(1_000)
        except Exception as e:
            print(e)

def __close_dialog(page: Page):
    try:
        dialog = page.locator(XpathSelectors.dialog)
        if dialog.count():
            close_btn = dialog.first.locator(XpathSelectors.close_btn)
            close_btn.click()
    except:
        pass

def __get_member_count(text: str) -> int:
    pattern = r"([\d.]+)([KkMm]?)\s+members"
    match = re.search(pattern, text)
    
    if not match:
        return 0
    
    number_part = float(match.group(1))
    unit_part = match.group(2).upper()
    
    # Chuyển đổi đơn vị
    if unit_part == 'K':
        return int(number_part * 1000)
    elif unit_part == 'M':
        return int(number_part * 1000000)
    
    return int(number_part)