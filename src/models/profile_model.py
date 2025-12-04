from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtCore import Qt, QModelIndex, QSortFilterProxyModel, QRegularExpression
from PyQt6.QtGui import QBrush, QColor
from typing import Any

from src.models._base_model import BaseModel, BaseProxyModel
from src.my_constants import DB_TABLES

PROFILE_TABLE = DB_TABLES["profile"]
PROFILE_LIVE = "live"
PROFILE_DEAD = "dead"

class Profile_Model(BaseModel):
	def __init__(self, db, parent=None):
		super().__init__(db, PROFILE_TABLE, parent)

	def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
		if not index.isValid():
			return None
		if role == Qt.ItemDataRole.ForegroundRole:
			return QBrush(QColor("black"))
		if role == Qt.ItemDataRole.BackgroundRole:
			status_col = self.fieldIndex("status")
			if status_col != -1:
				status_index = self.index(index.row(), status_col)
				status_value = super().data(status_index, Qt.ItemDataRole.DisplayRole)
				try:
					if status_value == PROFILE_DEAD:
						return QBrush(QColor("#e7625f"))
				except (ValueError, TypeError):
					pass
			return QBrush(QColor("#d3eaf2" if index.row() % 2 == 0 else "#f8e3ec"))
		return super().data(index, role)

class Profile_ProxyModel(BaseProxyModel):
	def __init__(self, db, parent=None):
		self.source = Profile_Model(db)
		super().__init__(source_model=self.source, parent=parent)
