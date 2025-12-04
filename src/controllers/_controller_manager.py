# src/controllers/_controller_manager.py

from src.services._service_manager import Service_Manager
from src.controllers._base_controller import BaseController
from src.controllers.profile_controller import Profile_Controller
from src.controllers.property_product_controller import PropertyProduct_Controller
from src.controllers.misc_product_controller import MiscProduct_Controller
from src.controllers.property_template_controller import PropertyTemplate_Controller
from src.controllers.setting_controller import Setting_Controller
from src.controllers.robot_controller import Robot_Controller


class Controller_Manager:
    def __init__(self, service_manager: Service_Manager):
        self.service_manager = service_manager
        
        self.profile_controller = Profile_Controller(service_manager)
        self.property_product_controller = PropertyProduct_Controller(service_manager)
        self.misc_product_controller = MiscProduct_Controller(service_manager)
        self.property_template_controller = PropertyTemplate_Controller(service_manager)
        self.setting_controller = Setting_Controller(service_manager)
        self.robot_controller = Robot_Controller(service_manager)
        self.base_controller = BaseController(service_manager)