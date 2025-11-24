# src/controllers/property_template_controller.py

from typing import Dict, Any, Union, Optional, List, Tuple
from src.utils.logger import Logger
from src.services._service_manager import Service_Manager
from src.my_types import PropertyTemplate_Type
from dataclasses import asdict


class InvalidInputError(Exception): pass
class TemplateNotFoundError(Exception): pass


class PropertyTemplate_Controller:
    def __init__(self, service_manager: Service_Manager):
        self.template_service = service_manager.property_template_service
        self.logger = Logger(self.__class__.__name__)

    def create(self, request_data: Dict[str, Any]) -> Union[PropertyTemplate_Type, Tuple[bool, str]]:
        try:
            required_fields = ["value"]
            for field in required_fields:
                if not request_data.get(field):
                    raise InvalidInputError(f"Required field '{field}' is missing.")
            
            payload = PropertyTemplate_Type(
                id=None, created_at=None, updated_at=None,
                transaction_type=request_data.get("transaction_type", 1),
                part=request_data.get("part", 1),
                category=request_data.get("category", 1),
                value=request_data["value"],
                is_default=request_data.get("is_default", False),
            )
            
            new_template = self.template_service.create(payload)
            
            if isinstance(new_template, PropertyTemplate_Type):
                return new_template 
            else:
                self.logger.error("Service failed to create property template.")
                return False, "Failed to create property template. Check service logs."
        
        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in create: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def read(self, template_id: str) -> Union[PropertyTemplate_Type, Tuple[bool, str]]:
        try:
            if not template_id:
                raise InvalidInputError("Template ID is required.")
                
            template = self.template_service.read(template_id)
            
            if isinstance(template, PropertyTemplate_Type):
                return template
            else:
                raise TemplateNotFoundError(f"Template with ID '{template_id}' not found.")
                
        except InvalidInputError as e:
            return False, str(e)
        except TemplateNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in read: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def update(self, template_id: str, update_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            if not template_id:
                raise InvalidInputError("Template ID is required for update.")
            if not update_data:
                raise InvalidInputError("Update data cannot be empty.")

            current_template = self.template_service.read(template_id)
            if not isinstance(current_template, PropertyTemplate_Type):
                raise TemplateNotFoundError(f"Template with ID '{template_id}' not found for update.")

            template_dict = asdict(current_template)
            template_dict.update(update_data)
            
            updated_payload = PropertyTemplate_Type(**template_dict)

            is_updated = self.template_service.update(updated_payload)

            if is_updated:
                return True, None
            else:
                error_msg = f"Service failed to update property template ID '{template_id}'."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except TemplateNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in update: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def delete(self, template_id: str) -> Tuple[bool, Optional[str]]:
        try:
            if not template_id:
                raise InvalidInputError("Template ID is required for delete.")

            is_deleted = self.template_service.delete(template_id)
            
            if is_deleted:
                return True, None
            else:
                error_msg = f"Failed to delete template with ID '{template_id}'. It may not exist."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in delete: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def read_all(self) -> List[PropertyTemplate_Type]:
        return self.template_service.read_all()