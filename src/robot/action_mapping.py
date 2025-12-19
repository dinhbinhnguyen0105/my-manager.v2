# src/robot/action_mapping.py
from src.my_constants import (
    SELL__BY_MARKETPLACE,
    SELL__BY_GROUP,
    DISCUSSION__TO_GROUP,
    DISCUSSION__TO_NEW_FEED,
    SHARE__BY_MOBILE,
    SHARE__BY_DESKTOP,
    LAUNCH,
    TAKE_CARE__JOIN_GROUP,
    GET_COOKIES
)

from src.robot.facebooks.launch import launch
from src.robot.facebooks.get_cookies import get_cookies

ACTION_MAPING = {
    LAUNCH : launch,
    GET_COOKIES: get_cookies
}