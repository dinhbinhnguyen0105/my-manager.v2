from src.models._base_model import BaseModel, BaseProxyModel
from src.my_constants import DB_TABLES

MISC_PRODUCT_TABLE = DB_TABLES["misc_product"]


class MiscProduct_Model(BaseModel):
	def __init__(self, db, parent=None):
		super().__init__(db, MISC_PRODUCT_TABLE, parent)


class MiscProduct_ProxyModel(BaseProxyModel):
	def __init__(self, db, parent=None):
		self.source = MiscProduct_Model(db)
		super().__init__(source_model=self.source, parent=parent)
