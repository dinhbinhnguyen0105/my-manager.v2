# src/utils/proxy_handler.py
import io, pycurl, json
from typing import Dict, Optional
from urllib.parse import urlparse

from src.utils.logger import Logger

def get_proxy(proxy_api: str) -> Optional[Dict[str, str]]:
    logger = Logger(__name__)
    try:
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, proxy_api.strip())
        curl.setopt(pycurl.CONNECTTIMEOUT, 60)
        curl.setopt(pycurl.TIMEOUT, 60)
        headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept: application/json, text/plain, */*",
            "Accept-Language: en-US,en;q=0.9",
            "Connection: keep-alive",
        ]
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.MAXREDIRS, 5)
        curl.perform()
        code = curl.getinfo(pycurl.RESPONSE_CODE)
        if code != 200:
            err_msg = f"Could not connect or receive a valid response. Server returned status code {code}"
            return False, err_msg
        body = buffer.getvalue().decode("utf-8")
        res = json.loads(body)
        proxyhttp = res.get("proxyhttp", None)
        if not proxyhttp:
            err_msg = f"Could not find 'proxyhttp' in the response ({res})"
            return False, err_msg
        else:
            ip, port, username, password = proxyhttp.split(":", 3)
            return True, {
                "username": username,
                "password": password,
                "server": f"{ip}:{port}"
            }    
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    proxy = get_proxy("https://api.proxyxoay.org//api/key_xoay.php?key=yT4gWhXmz3loXWDAMSGc")
    print(proxy)