# src/controllers/misc_product_controller.py

from typing import Dict, Any, Union, Optional, List, Tuple
from src.utils.logger import Logger
from src.services._service_manager import Service_Manager
from src.my_types import MiscProduct_Type
from dataclasses import asdict


class InvalidInputError(Exception): pass
class ProductNotFoundError(Exception): pass


class MiscProduct_Controller:
    def __init__(self, service_manager: Service_Manager):
        self.product_service = service_manager.misc_product_service
        self.logger = Logger(self.__class__.__name__)

    def create(self, request_data: Dict[str, Any]) -> Union[MiscProduct_Type, Tuple[bool, str]]:
        try:
            if not request_data.get("name"):
                raise InvalidInputError("Required field 'name' is missing.")
            
            payload = MiscProduct_Type(
                id=None, created_at=None, updated_at=None,
                status=request_data.get("status", True),
                name=request_data["name"],
                description=request_data.get("description"),
            )
            
            new_product = self.product_service.create(payload)
            
            if isinstance(new_product, MiscProduct_Type):
                return new_product 
            else:
                self.logger.error("Service failed to create misc product.")
                return False, "Failed to create misc product. Check service logs."
        
        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in create: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def read(self, product_id: str) -> Union[MiscProduct_Type, Tuple[bool, str]]:
        try:
            if not product_id:
                raise InvalidInputError("Product ID is required.")
                
            product = self.product_service.read(product_id)
            
            if isinstance(product, MiscProduct_Type):
                return product
            else:
                raise ProductNotFoundError(f"Product with ID '{product_id}' not found.")
                
        except InvalidInputError as e:
            return False, str(e)
        except ProductNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in read: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def update(self, product_id: str, update_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            if not product_id:
                raise InvalidInputError("Product ID is required for update.")
            if not update_data:
                raise InvalidInputError("Update data cannot be empty.")

            current_product = self.product_service.read(product_id)
            if not isinstance(current_product, MiscProduct_Type):
                raise ProductNotFoundError(f"Product with ID '{product_id}' not found for update.")

            product_dict = asdict(current_product)
            product_dict.update(update_data)
            
            updated_payload = MiscProduct_Type(**product_dict)

            is_updated = self.product_service.update(updated_payload)

            if is_updated:
                return True, None
            else:
                error_msg = f"Service failed to update misc product ID '{product_id}'."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except ProductNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in update: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def delete(self, product_id: str) -> Tuple[bool, Optional[str]]:
        try:
            if not product_id:
                raise InvalidInputError("Product ID is required for delete.")

            is_deleted = self.product_service.delete(product_id)
            
            if is_deleted:
                return True, None
            else:
                error_msg = f"Failed to delete product with ID '{product_id}'. It may not exist."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in delete: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def read_all(self) -> List[MiscProduct_Type]:
        return self.product_service.read_all()