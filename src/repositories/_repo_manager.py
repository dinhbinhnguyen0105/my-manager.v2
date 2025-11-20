# src/repositories/_repo_manager.py
from PyQt6.QtSql import QSqlDatabase

from src.repositories.misc_product_repo import MiscProduct_Repo
from src.repositories.profile_repo import Profile_Repo
from src.repositories.property_product_repo import PropertyProduct_Repo
from src.repositories.property_template_repo import PropertyTemplate_Repo
from src.repositories.setting_repo import Setting_Repo


class Repository_Manager:

    def __init__(self, db_instance: QSqlDatabase):
        self.misc_product_repo = MiscProduct_Repo(db_instance)
        self.profile_repo = Profile_Repo(db_instance)
        self.property_product_repo = PropertyProduct_Repo(db_instance)
        self.property_template_repo = PropertyTemplate_Repo(db_instance)
        self.setting_repo = Setting_Repo(db_instance)
