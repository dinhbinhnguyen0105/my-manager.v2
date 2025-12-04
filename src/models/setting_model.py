from src.models._base_model import BaseModel, BaseProxyModel
from src.my_constants import DB_TABLES

SETTING_TABLE = DB_TABLES["setting"]


class Setting_Model(BaseModel):
	def __init__(self, db, parent=None):
		super().__init__(db, SETTING_TABLE, parent)


class Setting_ProxyModel(BaseProxyModel):
	def __init__(self, db, parent=None):
			self.source = Setting_Model(db)
			super().__init__(source_model=self.source, parent=parent)
