# src/models/_base_model.py
from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtCore import Qt, QModelIndex, QSortFilterProxyModel, QRegularExpression
from PyQt6.QtGui import QBrush, QColor
from typing import Any
class BaseModel(QSqlTableModel):
    def __init__(self, db, table_name, parent=None):
        super().__init__(parent, db=db)
        self.setTable(table_name)
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)

    def reload_db(self):
        self.select()
        while self.canFetchMore():
            self.fetchMore()

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
                    if int(status_value) == 0:
                        return QBrush(QColor("#e7625f"))
                except (ValueError, TypeError):
                    pass
            return QBrush(QColor("#d3eaf2" if index.row() % 2 == 0 else "#f8e3ec"))
        return super().data(index, role)

class BaseProxyModel(QSortFilterProxyModel):
    """
    Base Proxy Model, inherits QSortFilterProxyModel.
    Wraps a BaseModel instance to provide sorting and filtering capabilities for Views.
    """
    def __init__(self, source_model: BaseModel, parent=None):
        super().__init__(parent)
        self.setSourceModel(source_model)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setDynamicSortFilter(True) # Quan trọng để lọc và sắp xếp nhanh

    def set_filter_column(self, column_index: int):
        """Đặt cột mà bộ lọc văn bản (text filter) sẽ áp dụng."""
        self.setFilterKeyColumn(column_index)

    def filter_by_text(self, text: str):
        """Lọc dữ liệu dựa trên văn bản và cột đã chọn."""
        # QRegExp là cách linh hoạt nhất để đặt bộ lọc văn bản
        # Escaping special characters and using a fixed string match (.*text.*)
        if text:
            escaped_text = QRegularExpression.escape(text)
            pattern = f".*{escaped_text}.*"
            regex = QRegularExpression(pattern)
            self.setFilterRegularExpression(regex)
        else:
            # Clear the filter
            self.setFilterRegularExpression(QRegularExpression())

    def sort_data(self, column_index: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        """Sắp xếp dữ liệu theo cột và thứ tự chỉ định."""
        self.sort(column_index, order)

    def get_source_model(self) -> BaseModel:
        """Trả về Source Model (BaseModel) đã bọc."""
        return self.sourceModel()