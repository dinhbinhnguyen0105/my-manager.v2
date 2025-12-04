# src/models/property_product_model.py
from src.models._base_model import BaseModel, BaseProxyModel
from src.my_constants import DB_TABLES

PROPERTY_PRODUCT_TABLE = DB_TABLES["property_product"]


class PropertyProduct_Model(BaseModel):
    def __init__(self, db, parent=None):
        super().__init__(db, PROPERTY_PRODUCT_TABLE, parent)


class PropertyProduct_ProxyModel(BaseProxyModel):
    def __init__(self, db, parent=None):
        self.source = PropertyProduct_Model(db)
        super().__init__(source_model=self.source, parent=parent)