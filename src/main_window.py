# src/views/main_window.py
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QLabel

from src.controllers._controller_manager import Controller_Manager
from src.models._model_manager import Model_Manager
from src.views.profiles.profiles_page import PageProfiles
from src.views.settings.settings_page import PageSettings
from src.views.properties.properties_page import PageProperties
from src.views.robot.robot_page import PageRobot

from src.ui.mainwindow_ui import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, controller_manager: Controller_Manager, model_manager: Model_Manager, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("My manager")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(960, 540)
        
        self.profiles_page = PageProfiles(controller_manager, model_manager)
        self.settings_page = PageSettings(controller_manager, model_manager)
        self.properties_page = PageProperties(controller_manager, model_manager)
        self.robot_page = PageRobot(controller_manager, model_manager)

        self.profiles_page.status_msg.connect(self.on_status_msg)
        self.robot_page.status_msg.connect(self.on_status_msg)

        self.permanent_label = QLabel()
        
        self.setup_UI()
        self.setup_events()
        self.setup_statusbar()

    
    def setup_UI(self):
        self.real_estate.setToolTip("Real estate products")
        self.misc.setToolTip("Misc products")
        self.profile.setToolTip("Facebook accounts")
        self.robot.setToolTip("Robot")
        self.template.setToolTip("Templates")
        self.setting.setToolTip("Settings")
        self.content_container.addWidget(self.properties_page)
        self.content_container.addWidget(self.settings_page)
        # _handle_list_more_place
        # self.content_container.addWidget(self.templates_page)
        # self.content_container.addWidget(self.misc_page)
        self.content_container.addWidget(self.profiles_page)
        self.content_container.addWidget(self.robot_page)
        self.content_container.setCurrentWidget(self.robot_page)
    def setup_events(self):
        self.setting.toggled.connect(lambda : self.content_container.setCurrentWidget(self.settings_page))
        self.profile.toggled.connect(lambda : self.content_container.setCurrentWidget(self.profiles_page))
        self.real_estate.toggled.connect(lambda : self.content_container.setCurrentWidget(self.properties_page))
        self.robot.toggled.connect(lambda : self.content_container.setCurrentWidget(self.robot_page))
        # self.real_estate.toggled.connect(self.content_container.setCurrentWidget())
    def setup_statusbar(self):
        self.status_bar.addWidget(self.permanent_label)
    

    @pyqtSlot(str)
    def on_status_msg(self, msg: str):
        self.permanent_label.setText(msg)