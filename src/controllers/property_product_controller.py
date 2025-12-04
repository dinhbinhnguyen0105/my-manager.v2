# src/controllers/property_product_controller.py

from typing import Dict, Any, Union, Optional, List, Tuple
from src.controllers._base_controller import BaseController
from src.services._service_manager import Service_Manager
from src.my_types import PropertyProduct_Type
from dataclasses import asdict
from src.utils.exception_handler import log_exception


class InvalidInputError(Exception): pass
class ProductNotFoundError(Exception): pass


class PropertyProduct_Controller(BaseController):
    def __init__(self, service_manager:Service_Manager):
        super().__init__(service_manager)

    def create(self, request_data: Dict[str, Any]) -> Union[PropertyProduct_Type, Tuple[bool, str]]:
        try:
            required_fields = ["street", "area", "price", "unit"]
            for field in required_fields:
                if not request_data.get(field):
                    raise InvalidInputError(f"Required field '{field}' is missing.")
            
            payload = PropertyProduct_Type(
                id=None, created_at=None, updated_at=None,
                pid=request_data.get("pid"),
                status=request_data.get("status", 1),
                transaction_type=request_data.get("transaction_type", 1),
                province=request_data.get("province", 1),
                district=request_data.get("district", 1),
                ward=request_data.get("ward", 1),
                street=request_data["street"],
                category=request_data.get("category", 1),
                area=request_data["area"],
                price=request_data["price"],
                unit=request_data["unit"],
                legal=request_data.get("legal", 1),
                structure=request_data.get("structure", 0.0),
                function=request_data.get("function"),
                building_line=request_data.get("building_line", 1),
                furniture=request_data.get("furniture", 1),
                description=request_data.get("description"),
            )
            
            new_product = self.service_manager.property_product_service.create(payload)
            
            if isinstance(new_product, PropertyProduct_Type):
                return new_product 
            else:
                self.logger.error("Service failed to create property product.")
                return False, "Failed to create property product. Check service logs."
        
        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in create: {e}"
            log_exception(e)
            return False, error_msg

    def read(self, product_id: str) -> Union[Dict[str, Any], Tuple[bool, str]]:
        try:
            if not product_id:
                raise InvalidInputError("Product ID is required.")
                
            product = self.service_manager.property_product_service.read(product_id)
            
            if isinstance(product.get("info"), PropertyProduct_Type):
                return product
            else:
                raise ProductNotFoundError(f"Product with ID '{product_id}' not found.")
                
        except InvalidInputError as e:
            return False, str(e)
        except ProductNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in read: {e}"
            log_exception(e)
            return False, error_msg

    def update(self, product_id: str, update_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            if not product_id:
                raise InvalidInputError("Product ID is required for update.")
            if not update_data:
                raise InvalidInputError("Update data cannot be empty.")

            current_product = self.service_manager.property_product_service.read(product_id)
            if not isinstance(current_product, PropertyProduct_Type):
                raise ProductNotFoundError(f"Product with ID '{product_id}' not found for update.")

            product_dict = asdict(current_product)
            product_dict.update(update_data)
            
            updated_payload = PropertyProduct_Type(**product_dict)

            is_updated = self.service_manager.property_product_service.update(updated_payload)

            if is_updated:
                return True, None
            else:
                error_msg = f"Service failed to update property product ID '{product_id}'."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except ProductNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in update: {e}"
            log_exception(e)
            return False, error_msg
    def change_status(self, id: str, status: str):
        try:
            if not id:
                raise InvalidInputError("Product ID is required for update.")
            if not status:
                raise InvalidInputError("Update data cannot be empty.")

            current_product = self.service_manager.property_product_service.read(id)
            if not isinstance(current_product.get("info"), PropertyProduct_Type):
                raise ProductNotFoundError(f"Product with ID '{id}' not found for update.")
            return self.service_manager.property_product_service.change_status(id, status)
        except Exception as e:
            log_exception(e)
            return False
        
    def delete(self, product_id: str) -> Tuple[bool, Optional[str]]:
        try:
            if not product_id:
                raise InvalidInputError("Product ID is required for delete.")

            is_deleted = self.service_manager.property_product_service.delete(product_id)
            
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
            log_exception(e)
            return False, error_msg

    def read_all(self) -> List[Dict[str, Any]]:
        return self.service_manager.property_product_service.read_all()
    
    def get_random(self, transaction_type: str, days: int) -> Optional[Dict[str, Any]]:
        return self.service_manager.property_product_service.get_random(transaction_type, days)
    
    def import_data(self,file_path: str, data_format: str) -> Tuple[bool, Optional[str]]:
        return super().import_data("property_product_service", file_path, data_format)
    def export_data(self, file_path, data_format = "json"):
        return super().export_data("property_product_service", file_path, data_format)