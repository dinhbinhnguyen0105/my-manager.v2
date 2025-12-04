from src.models._base_model import BaseModel, BaseProxyModel
from src.my_constants import DB_TABLES

PROPERTY_TEMPLATE_TABLE = DB_TABLES["property_template"]


class PropertyTemplate_Model(BaseModel):
	def __init__(self, db, parent=None):
		super().__init__(db, PROPERTY_TEMPLATE_TABLE, parent)


class PropertyTemplate_ProxyModel(BaseProxyModel):
	def __init__(self, db, parent=None):
			self.source = PropertyTemplate_Model(db)
			super().__init__(source_model=self.source, parent=parent)
