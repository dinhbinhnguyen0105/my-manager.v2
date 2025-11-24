# src/services/misc_product_service.py
import os
from random import randint, choice
from typing import Optional, List, Union, Dict, Any, Tuple
from datetime import datetime
from PIL import Image

# Giả định các import cần thiết từ các file bạn đã cung cấp
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
    """
    Service layer for MiscProduct, handling business logic and coordinating with the Repository.
    """

    def create(
        self, product_payload: MiscProduct_Type, image_paths: List[str]
    ) -> Union[MiscProduct_Type, bool]:
        """
        Creates a new miscellaneous product and handles image processing.
        """
        new_product = self.repo_manager.misc_product_repo.insert(product_payload)
        if not new_product:
            self.logger.error("Failed to insert misc product into repository.")
            return False

        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        if not image_container or not os.path.exists(image_container):
            self.logger.error(f"Image container directory not found: {image_container}. Aborting image processing.")
            return False

        current_image_dir = os.path.join(image_container, str(new_product.id))
        current_image_source_dir = os.path.join(current_image_dir, f"{str(new_product.id)}_source")
        current_image_logo_dir = os.path.join(current_image_dir, f"{str(new_product.id)}_logo")
        
        os.makedirs(current_image_source_dir, exist_ok=True)
        os.makedirs(current_image_logo_dir, exist_ok=True)

        copy_source_images(image_paths, current_image_source_dir)
        
        insert_logo_to_images(
            image_paths, LOGO_FILE, current_image_logo_dir, str(new_product.id), 0.7
        )

        self.logger.info(f"Misc product created successfully: {new_product.id}")
        return new_product

    def update(self, product_payload: MiscProduct_Type) -> bool:
        """
        Updates an existing miscellaneous product record.
        """

        is_updated = self.repo_manager.misc_product_repo.update_product(product_payload)
        if is_updated:
            self.logger.info(f"Misc product updated successfully: {product_payload.id}")
            return True
        self.logger.error(f"Failed to update misc product: {product_payload.id}")
        return False
    def refresh(self, product_id: str) -> bool:
        """Refreshes the 'updated_at' timestamp for a misc product record."""
        is_refreshed = self.repo_manager.misc_product_repo.refresh_updated_at(
            product_id
        )
        if is_refreshed:
            self.logger.info(
                f"Successfully refreshed updated_at for MiscProduct with ID: {product_id}"
            )
            return True
        else:
            self.logger.error(
                f"Failed to refresh updated_at for MiscProduct with ID: {product_id}"
            )
            return False

    def delete(self, product_id: str) -> bool:
        """
        Deletes a miscellaneous product and its associated image folders.
        """
        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        current_image_dir = os.path.join(image_container, product_id)
        
        if not remove_images(current_image_dir):
            self.logger.warning(f"Failed to remove image directory for misc product: {product_id}. Proceeding with DB deletion.")
        
        is_deleted = self.repo_manager.misc_product_repo.delete_product_by_id(product_id)
        
        if is_deleted:
            self.logger.info(f"Misc product deleted successfully: {product_id}")
            return True
        else:
            self.logger.error(f"Failed to delete misc product from DB: {product_id}")
            return False

    def read(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single miscellaneous product record by ID.
        """
        current_product = self.repo_manager.misc_product_repo.get_product_by_id(product_id)
        if not current_product:
            self.logger.warning(f"Misc product not found with ID: {product_id}")
            return None
        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        current_image_dir = os.path.join(image_container, str(current_product.id))
        current_image_logo_dir = os.path.join(current_image_dir, f"{str(current_product.id)}_logo")
        current_product_imgs = get_images(current_image_logo_dir)
        return {
            "info": current_product,
            "image_paths": current_product_imgs
        }

    def read_all(self) -> List[Dict[str, Any]]:
        """
        Retrieves all miscellaneous product records.
        """
        results = []
        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        list_of_product = self.repo_manager.misc_product_repo.get_all_products()
        for product in list_of_product:
            current_image_dir = os.path.join(image_container, str(product.id))
            current_image_logo_dir = os.path.join(current_image_dir, f"{str(product.id)}_logo")
            current_product_imgs = get_images(current_image_logo_dir)
            results.append({
                "info": product,
                "image_paths": current_product_imgs
            })

        return results

    def read_all_for_export(self) -> List[Dict[str, Any]]:
        """
        Retrieves all miscellaneous product records in dictionary format for export/display.
        """
        
        return self.repo_manager.misc_product_repo.get_all_for_export()
    
    def create_bulk(self, product_list: List[MiscProduct_Type]) -> bool:
        """
        Inserts multiple MiscProduct_Type records in a single database transaction.
        Image handling for bulk inserts is typically deferred or handled externally.
        """
        if not product_list:
            return True
        
        success = self.repo_manager.misc_product_repo.insert_bulk_products(product_list)
        if success:
            self.logger.info(f"Successfully inserted {len(product_list)} misc products in bulk.")
        else:
            self.logger.error(f"Failed to insert misc products in bulk. Transaction rolled back.")
        return success