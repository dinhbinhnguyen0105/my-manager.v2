# src/services/property_template_service.py

from typing import Optional, List, Union, Dict, Any
from dataclasses import asdict

from src.my_types import PropertyTemplate_Type
from src.services._base_service import BaseService


class PropertyTemplate_Service(BaseService):
    """
    Service layer for PropertyTemplate, handling business logic.
    """

    def _dict_to_data_type(self, data: Dict[str, Any]) -> PropertyTemplate_Type:
        """Converts a database dictionary record into a PropertyTemplate_Type dataclass."""
        required_keys = [
            field.name for field in PropertyTemplate_Type.__dataclass_fields__.values()
        ]
        return PropertyTemplate_Type(**{key: data.get(key) for key in required_keys})

    def create(self, template_payload: PropertyTemplate_Type) -> Union[PropertyTemplate_Type, bool]:
        """
        Creates a new property template record.
        """
        new_template = self.repo_manager.property_template_repo.insert(template_payload)
        if new_template:
            self.logger.info(f"Property template created successfully: {new_template.id}")
            return new_template
        self.logger.error("Failed to insert property template into repository.")
        return False

    def update(self, template_payload: PropertyTemplate_Type) -> bool:
        """
        Updates an existing property template record.
        """
        is_updated = self.repo_manager.property_template_repo.update_template(template_payload)
        if is_updated:
            self.logger.info(f"Property template updated successfully: {template_payload.id}")
            return True
        self.logger.error(f"Failed to update property template: {template_payload.id}")
        return False
    
    def change_status(self, id: str, status: str):
        is_updated = self.repo_manager.property_template_repo.change_status(id, status)
        if is_updated:
            self.logger.info(f"Property template updated successfully: {id}")
            return True
        self.logger.error(f"Failed to update property template: {id}")
        return False

    def delete(self, template_id: str) -> bool:
        """
        Deletes a property template record by ID.
        """
        is_deleted = self.repo_manager.property_template_repo.delete_template_by_id(template_id)
        if is_deleted:
            self.logger.info(f"Property template deleted successfully: {template_id}")
            return True
        self.logger.error(f"Failed to delete property template from DB: {template_id}")
        return False

    def read(self, template_id: str) -> Optional[PropertyTemplate_Type]:
        """
        Retrieves a single property template record by ID.
        """
        return self.repo_manager.property_template_repo.get_template_by_id(template_id)

    def read_all(self) -> List[PropertyTemplate_Type]:
        """
        Retrieves all property template records.
        """
        return self.repo_manager.property_template_repo.get_all_templates()
    
    def get_random(self, transaction_type:str, name:str, category:str, is_default: bool = True)-> Optional[PropertyTemplate_Type]:
        current_templ = self.repo_manager.property_template_repo.get_random_template_by_filters(transaction_type, name, category, is_default)
        if not current_templ:
            self.logger.warning(f"Không tìm thấy product phù hợp với transaction = {transaction_type}, name = {name}, category = {category}")
            return None
        return current_templ

    def read_all_for_export(self) -> List[Dict[str, Any]]:
        """
        Retrieves all property template records in dictionary format for export/display.
        """
        return self.repo_manager.property_template_repo.get_all_for_export()
    
    def create_bulk(self, payload: List[PropertyTemplate_Type]) -> bool:
        """
        Inserts multiple PropertyTemplate_Type records in a single database transaction.
        """
        if not payload:
            return True
        
        # Repo method name là insert_bulk_products nhưng xử lý PropertyTemplate_Type
        success = self.repo_manager.property_template_repo.insert_bulk(payload)
        if success:
            self.logger.info(f"Successfully inserted {len(payload)} property templates in bulk.")
        else:
            self.logger.error(f"Failed to insert property templates in bulk. Transaction rolled back.")
        return success