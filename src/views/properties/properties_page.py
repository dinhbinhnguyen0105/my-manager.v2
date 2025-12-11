# src/views/properties/properties_page.py
from typing import  Any, Dict, List, Tuple
from PyQt6.QtWidgets import QWidget, QLineEdit, QMenu
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    QPoint,
    QItemSelection,
    QItemSelectionModel,
)
from PyQt6.QtGui import QAction, QShortcut, QKeySequence

from src.controllers._controller_manager import Controller_Manager
from src.models._model_manager import Model_Manager
from src.views.utils.display_order_filter import (
    apply_display_order_filter,
    prune_hidden_selection,
)
from src.views.utils.import_export_handler import ImportExportHandler

from src.ui.page_properties_ui import Ui_PageProperties

class PageProperties(QWidget, Ui_PageProperties):
    def __init__(self, controller_manager: Controller_Manager, model_manager: Model_Manager, parent = None):
        super(PageProperties, self).__init__(parent=None)
        self.setupUi(self)
        self.setWindowTitle("properties page".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.controller_manager = controller_manager
        self.model_manager = model_manager
        self.proxy_model = self.model_manager.property_product()
        self.base_model = self.proxy_model.get_source_model()
        self.import_export_handler = ImportExportHandler(self.controller_manager.property_product_controller, self.properties_table)
        self.setup_table()
        self.setup_connections()
        self.setup_filters()
        self.setup_shortcuts()
    
    def setup_table(self):
        self.properties_table.setModel(self.proxy_model)
        self.properties_table.setSortingEnabled(True)
        created_at_col_index = self.base_model.fieldIndex("created_at")
        if created_at_col_index != -1:
            self.base_model.sort(
                created_at_col_index,
                Qt.SortOrder.DescendingOrder,  # Sắp xếp giảm dần (mới nhất lên trên)
            )
        self.display_table_columns()
        self.properties_table.setSelectionBehavior(
            self.properties_table.SelectionBehavior.SelectRows
        )
        self.properties_table.setEditTriggers(
            self.properties_table.EditTrigger.NoEditTriggers
        )
        self.properties_table.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self.properties_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.properties_table.customContextMenuRequested.connect(
            self._set_table_context_menu
        )
    
    def display_table_columns(self):
        columns_to_display = [
            "uid",
            "username",
            "password",
            "two_fa",
            "profile_note",
            "profile_type",
            "profile_group",
            "profile_name",
            "created_at",
        ]

        for col in range(self.base_model.columnCount()):
            column_name = self.base_model.headerData(col, Qt.Orientation.Horizontal)
            if column_name not in columns_to_display:
                self.properties_table.setColumnHidden(col, True)
            else:
                self.properties_table.setColumnHidden(col, False)
    
    def get_selected_ids(self):
        selected_rows_indexes = (
            self.properties_table.selectionModel().selectedRows()
        )
        selected_ids = []
        id_col = self.base_model.fieldIndex("id")
        if id_col == -1:
            return []
        for proxy_index in selected_rows_indexes:
            if self.properties_table.isRowHidden(proxy_index.row()):
                continue
            source_index = self.proxy_model.mapToSource(proxy_index)
            id_index = self.base_model.index(source_index.row(), id_col)
            id_value = self.base_model.data(id_index, Qt.ItemDataRole.DisplayRole)
            if id_value:
                selected_ids.append(id_value)

        return selected_ids
        
    @pyqtSlot(QPoint)
    def _set_table_context_menu(self, pos: QPoint):
        proxy_index = self.properties_table.indexAt(pos)
        if not proxy_index.isValid():
            return
        global_pos = self.properties_table.mapToGlobal(pos)

        menu = QMenu(self.properties_table)
        launch_as_desktop = QAction("Launch as desktop", self)
        launch_as_mobile = QAction("Launch as mobile", self)
        check_live = QAction("Check live", self)
        change_to_live = QAction("Change to live", self)
        change_to_dead = QAction("Change to dead", self)
        update = QAction("Update", self)
        delete = QAction("Delete", self)
        menu.addAction(launch_as_desktop)
        menu.addAction(launch_as_mobile)
        menu.addAction(check_live)
        menu.addAction(change_to_live)
        menu.addAction(change_to_dead)
        menu.addAction(update)
        menu.addAction(delete)
        launch_as_desktop.triggered.connect(self._on_launch_as_desktop)
        launch_as_mobile.triggered.connect(self._on_launch_as_mobile)
        check_live.triggered.connect(self._on_check_live)
        change_to_live.triggered.connect(self._on_change_to_live)
        change_to_dead.triggered.connect(self._on_change_to_dead)
        update.triggered.connect(self._on_update)
        delete.triggered.connect(self._on_delete)
        menu.popup(global_pos)
    
    @pyqtSlot(QItemSelection, QItemSelection)
    def _on_selection_changed(
        self, selected: QItemSelection, deselected: QItemSelection
    ):
        sel_model = self.properties_table.selectionModel()
        hidden_to_deselect = []
        for proxy_index in sel_model.selectedRows():
            try:
                if self.properties_table.isRowHidden(proxy_index.row()):
                    hidden_to_deselect.append(proxy_index)
            except Exception:
                pass

        if hidden_to_deselect:
            for idx in hidden_to_deselect:
                sel_model.select(
                    idx,
                    QItemSelectionModel.SelectionFlag.Deselect
                    | QItemSelectionModel.SelectionFlag.Rows,
                )
   
    def setup_connections(self):
        self.action_create_btn.clicked.connect(self._on_create_btn_clicked)
        self.action_import_btn.clicked.connect(self._handle_import)
        self.action_export_btn.clicked.connect(self._handle_export)
        self.action_default_btn.clicked.connect(self._on_default_btn_clicked)
        self.action_random_btn.clicked.connect(self._on_random_btn_clicked)
        self.action_rewrite_by_ai_btn.clicked.connect(self._on_rewrite_by_ai_btn_clicked)
    
    def setup_filters(self):pass
    def setup_shortcuts(self):
        create_new = QShortcut(QKeySequence("Ctrl+N"), self)
        delete_1 = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Backspace), self
        )
        delete_2 = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Delete), self)
        _import = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_I), self)
        _export = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_E), self)

        create_new.activated.connect(self._on_create_btn_clicked)
        delete_1.activated.connect(self._on_delete)
        delete_2.activated.connect(self._on_delete)
        _import.activated.connect(self._handle_import)
        _export.activated.connect(self._handle_export)


    @pyqtSlot()
    def _on_delete(self): pass
    @pyqtSlot()
    def _on_create_btn_clicked(self): pass
    @pyqtSlot()
    def _handle_import(self): pass
    @pyqtSlot()
    def _handle_export(self): pass
    @pyqtSlot()
    def _on_default_btn_clicked(self): pass
    @pyqtSlot()
    def _on_random_btn_clicked(self): pass
    @pyqtSlot()
    def _on_rewrite_by_ai_btn_clicked(self): pass
