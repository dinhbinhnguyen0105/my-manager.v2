# src/utils/proxy_handler.py
import io, pycurl, json
from typing import Dict, Optional
from urllib.parse import urlparse


def get_proxy(proxy_api: str) -> Optional[Dict[str, str]]:
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
        proxysocks5 = res.get("proxysocks5", None)
        current_ip = res.get("ip", None)
        status = res.get("status", 400)
        
        if not proxyhttp:
            err_msg = f"Could not find 'proxyhttp' in the response ({res})"
            return False, err_msg
        else:
            return True, {
                "proxyhttp": proxyhttp, "proxysocks5": proxysocks5, "current_ip" : current_ip, "status": status, "message": str(res)
            }
    except Exception as e:
        return False, str(e)
    