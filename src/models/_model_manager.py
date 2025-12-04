from typing import Dict

from src.models.profile_model import Profile_ProxyModel
from src.models.property_product_model import PropertyProduct_ProxyModel
from src.models.misc_product_model import MiscProduct_ProxyModel
from src.models.property_template_model import PropertyTemplate_ProxyModel
from src.models.setting_model import Setting_ProxyModel


class Model_Manager:
	"""Simple factory/registry for model instances.

	Holds single instances per model type for reuse by controllers/views.
	"""

	def __init__(self, db):
		self.db = db
		self._instances: Dict[str, object] = {}

	def profile(self) -> Profile_ProxyModel:
		if "profile" not in self._instances:
			self._instances["profile"] = Profile_ProxyModel(self.db)
		return self._instances["profile"]

	def property_product(self) -> PropertyProduct_ProxyModel:
		if "property_product" not in self._instances:
			self._instances["property_product"] = PropertyProduct_ProxyModel(self.db)
		return self._instances["property_product"]

	def misc_product(self) -> MiscProduct_ProxyModel:
		if "misc_product" not in self._instances:
			self._instances["misc_product"] = MiscProduct_ProxyModel(self.db)
		return self._instances["misc_product"]

	def property_template(self) -> PropertyTemplate_ProxyModel:
		if "property_template" not in self._instances:
			self._instances["property_template"] = PropertyTemplate_ProxyModel(self.db)
		return self._instances["property_template"]

	def setting(self) -> Setting_ProxyModel:
		if "setting" not in self._instances:
			self._instances["setting"] = Setting_ProxyModel(self.db)
		return self._instances["setting"]
