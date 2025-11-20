# src/services/misc_product_service.py

from random import randint, choice
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
from PIL import Image

from src.my_types import MiscProduct_Type
from utils.image_handlers import (
    copy_source_images,
    insert_logo_to_images,
    remove_images,
    get_images,
)
from src.services._base_service import BaseService
from src.my_constants import SETTING_NAME_OPTIONS

IMAGE_CONTAINER_DIR = SETTING_NAME_OPTIONS["image_container_dir"]
LOGO_FILE = SETTING_NAME_OPTIONS["logo_file"]


class MiscProduct_Service(BaseService):
    def create(
        self, product_payload: MiscProduct_Type, image_paths: List[str]
    ) -> Union[MiscProduct_Type, bool]:
        new_product = self.repo_manager.misc_product_repo.insert(product_payload)
        if not new_product:
            return False
        insert_logo
