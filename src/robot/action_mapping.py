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
)

from src.robot.facebooks.launch import launch


ACTION_MAPING = {
    LAUNCH : launch
}