import json, os
from src.my_constants import COOKIES_PATH
def write_cookies(uid: str, cookies: str) -> bool:
    data = {}
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, "r") as f:
            contents = f.read()
            if contents: 
                data = json.loads(contents)
    data[uid] = cookies
    with open(COOKIES_PATH, "w") as f:
        json.dump(data, f, indent=4)
    
    return True
    
def read_cookies(uid: str) -> str:
    data = {}
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, "r") as f:
            contents = f.read()
            if contents: 
                data = json.loads(contents)
    return data.get(uid)