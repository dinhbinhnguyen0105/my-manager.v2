from src.database._database_manager import DatabaseManager
from src.models._model_manager import Model_Manager
from src.repositories._repo_manager import Repository_Manager
from src.services._service_manager import Service_Manager
from src.controllers._controller_manager import Controller_Manager

from src.views.main_window import MainWindow

class Application:
    def __init__(self):
        self.db_manager = DatabaseManager()
        db = self.db_manager.get_db()
        self.model_manager = Model_Manager(db)
        self.repo_manager = Repository_Manager(db)
        self.service_manager = Service_Manager(self.repo_manager)
        self.controller_manager = Controller_Manager(self.service_manager)
        self.main_window = MainWindow(self.controller_manager, self.model_manager)
        self.main_window.show()