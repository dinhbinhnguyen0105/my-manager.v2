# src/services/_service_manager.py

from src.repositories._repo_manager import Repository_Manager
from src.services.misc_product_service import MiscProduct_Service
from src.services.profile_service import Profile_Service
from src.services.property_product_service import PropertyProduct_Service
from src.services.property_template_service import PropertyTemplate_Service
from src.services.setting_service import Setting_Service


class Service_Manager:
    """
    A centralized manager to hold and provide access to all service layer instances.
    It links the application logic layer (Service) with the data access layer (Repository).
    """
    def __init__(self, repo_manager: Repository_Manager):
        """
        Initializes all service classes, injecting the Repository_Manager dependency.
        """
        self.misc_product_service = MiscProduct_Service(repo_manager)
        self.profile_service = Profile_Service(repo_manager)
        self.property_product_service = PropertyProduct_Service(repo_manager)
        self.property_template_service = PropertyTemplate_Service(repo_manager)
        self.setting_service = Setting_Service(repo_manager)