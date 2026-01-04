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
    TAKE_CARE__ADD_FRIEND,
    TAKE_CARE__COMMENT_TO_GROUP,
    TAKE_CARE__COMMENT_TO_FRIEND_WALL,
    GET_COOKIES
)

from src.robot.facebooks.launch import launch
from src.robot.facebooks.get_cookies import get_cookies
from src.robot.facebooks.join_groups import join_groups
from src.robot.facebooks.add_friends import add_friends

ACTION_MAPING = {
    LAUNCH : launch,
    GET_COOKIES: get_cookies,
    TAKE_CARE__JOIN_GROUP: join_groups,
    TAKE_CARE__ADD_FRIEND: add_friends,
}