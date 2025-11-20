# src/my_types.py

from dataclasses import dataclass
from typing import Optional, List, Union, Any, Dict


@dataclass
class Profile_Type:
    id: Optional[str]
    mobile_ua: str
    desktop_ua: str
    uid: Optional[str]
    status: int
    username: Optional[str]
    password: Optional[str]
    two_fa: Optional[str]
    email: Optional[str]
    email_password: Optional[str]
    phone_number: Optional[str]
    profile_note: Optional[str]
    profile_type: Optional[str]
    profile_group: Optional[int]
    profile_name: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class PropertyProduct_Type:
    id: Optional[str]
    pid: Optional[str]
    status: int
    transaction_type: int
    province: int
    district: int
    ward: int
    street: str
    category: int
    area: float
    price: float
    unit: str
    legal: int
    structure: float
    function: str
    building_line: int
    furniture: int
    description: str
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class PropertyTemplate_Type:
    id: Optional[str]
    transaction_type: int
    part: int
    category: int
    value: str
    is_default: bool
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class MiscProduct_Type:
    id: Optional[str]
    status: bool
    name: str
    description: str
    created_at: Optional[str]
    updated_at: Optional[str]


@dataclass
class Setting_Type:
    id: Optional[str]
    name: str
    value: str
    is_selected: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class Statuses:
    worker_finished = "WORKER_FINISHED"
