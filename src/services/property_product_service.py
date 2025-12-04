# src/services/property_product_service.py

import os
from typing import Optional, List, Union, Dict, Any, Tuple
from dataclasses import asdict

from src.my_types import PropertyProduct_Type
from src.services._base_service import BaseService
from src.utils.image_handlers import (
    copy_source_images,
    insert_logo_to_images,
    remove_images,
    get_images,
)


IMAGE_CONTAINER_DIR = "image_container_dir"
LOGO_FILE = "logo_file"


class PropertyProduct_Service(BaseService):
    """
    Service layer for PropertyProduct, handling business logic and image file system coordination.
    """

    def _dict_to_data_type(self, data: Dict[str, Any]) -> PropertyProduct_Type:
        """Converts a database dictionary record into a PropertyProduct_Type dataclass."""
        required_keys = [
            field.name for field in PropertyProduct_Type.__dataclass_fields__.values()
        ]
        return PropertyProduct_Type(**{key: data.get(key) for key in required_keys})

    def create(
        self, product_payload: PropertyProduct_Type, image_paths: List[str]
    ) -> Union[PropertyProduct_Type, bool]:
        """
        Creates a new property product and handles image processing.
        """
        # 1. Insert product data into the database
        new_product = self.repo_manager.property_product_repo.insert(product_payload)
        if not new_product:
            self.logger.error("Failed to insert property product into repository.")
            return False

        # 2. Handle image container setup
        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        if not image_container or not os.path.exists(image_container):
            self.logger.error(f"Image container directory not found: {image_container}. Aborting image processing.")
            # Rollback DB insert
            self.repo_manager.property_product_repo.delete_product_by_id(new_product.id)
            return False

        # 3. Define and create product-specific image directories
        product_id_str = str(new_product.id)
        current_image_dir = os.path.join(image_container, product_id_str)
        current_image_source_dir = os.path.join(current_image_dir, f"{product_id_str}_source")
        current_image_logo_dir = os.path.join(current_image_dir, f"{product_id_str}_logo")
        
        os.makedirs(current_image_source_dir, exist_ok=True)
        os.makedirs(current_image_logo_dir, exist_ok=True)

        # 4. Copy source images
        copy_source_images(image_paths, current_image_source_dir)
        
        # 5. Insert logo (process image)
        insert_logo_to_images(
            image_paths, LOGO_FILE, current_image_logo_dir, product_id_str, 0.7
        )

        self.logger.info(f"Property product created successfully: {new_product.id}")
        return new_product

    def update(self, product_payload: PropertyProduct_Type) -> bool:
        """
        Updates an existing property product record.
        """
        is_updated = self.repo_manager.property_product_repo.update_product(product_payload)
        if is_updated:
            self.logger.info(f"Property product updated successfully: {product_payload.id}")
            return True
        self.logger.error(f"Failed to update property product: {product_payload.id}")
        return False
    
    def change_status(self, id: str, status: str):
        is_updated = self.repo_manager.property_product_repo.change_status(id, status)
        if is_updated:
            self.logger.info(f"Property product updated successfully: {id}")
            return True
        self.logger.error(f"Failed to update property product: {id}")
        return False
    
    def refresh(self, product_id: str) -> bool:
        """Refreshes the 'updated_at' timestamp for a property product record."""
        is_refreshed = self.repo_manager.property_product_repo.refresh_updated_at(
            product_id
        )
        if is_refreshed:
            self.logger.info(
                f"Successfully refreshed updated_at for PropertyProduct with ID: {product_id}"
            )
            return True
        else:
            self.logger.error(
                f"Failed to refresh updated_at for PropertyProduct with ID: {product_id}"
            )
            return False
    def delete(self, product_id: str) -> bool:
        """
        Deletes a property product and its associated image folders.
        """
        # 1. Get image container path
        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        current_image_dir = os.path.join(image_container, product_id)
        
        # 2. Remove associated image files
        if not remove_images(current_image_dir):
            self.logger.warning(f"Failed to remove image directory for property product: {product_id}. Proceeding with DB deletion.")
        
        # 3. Delete product from database
        is_deleted = self.repo_manager.property_product_repo.delete_product_by_id(product_id)
        
        if is_deleted:
            self.logger.info(f"Property product deleted successfully: {product_id}")
            return True
        else:
            self.logger.error(f"Failed to delete property product from DB: {product_id}")
            return False

    def read(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single property product record by ID.
        """
        current_product = self.repo_manager.property_product_repo.get_product_by_id(product_id)
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
        Retrieves all property product records.
        """
        results = []
        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        list_of_product = self.repo_manager.property_product_repo.get_all_products()
        for product in list_of_product:
            current_image_dir = os.path.join(image_container, str(product.id))
            current_image_logo_dir = os.path.join(current_image_dir, f"{str(product.id)}_logo")
            current_product_imgs = get_images(current_image_logo_dir)
            results.append({
                "info": product,
                "image_paths": current_product_imgs
            })

        return results

    def get_random(self, transaction, days) -> Optional[Dict[str, Any]]:
        current_product = self.repo_manager.property_product_repo.get_random_product_by_transaction_and_update_days(transaction, days)
        if not current_product:
            self.logger.warning(f"Không tìm thấy product phù hợp với transaction = {transaction}, days = {days}")
            return None
        image_container = self.repo_manager.setting_repo.get_setting_value_by_name(IMAGE_CONTAINER_DIR)
        current_image_dir = os.path.join(image_container, str(current_product.id))
        current_image_logo_dir = os.path.join(current_image_dir, f"{str(current_product.id)}_logo")
        current_product_imgs = get_images(current_image_logo_dir)
        return {
            "info": current_product,
            "image_paths": current_product_imgs
        }
    
    def read_all_for_export(self) -> List[Dict[str, Any]]:
        """
        Retrieves all property product records in dictionary format for export/display.
        """
        return self.repo_manager.property_product_repo.get_all_for_export()
    
    def create_bulk(self, payload: List[PropertyProduct_Type]) -> bool:
        """
        Inserts multiple PropertyProduct_Type records in a single database transaction.
        """
        if not payload:
            return True
        
        success = self.repo_manager.property_product_repo.insert_bulk(payload)
        if success:
            self.logger.info(f"Successfully inserted {len(payload)} property products in bulk.")
        else:
            self.logger.error(f"Failed to insert property products in bulk. Transaction rolled back.")
        return success