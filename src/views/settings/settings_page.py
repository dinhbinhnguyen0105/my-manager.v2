# src/views/settings/settings_page.py
from PyQt6.QtWidgets import QWidget, QMenu, QFileDialog
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    QPoint,
    QItemSelection,
    QItemSelectionModel,
)
from PyQt6.QtGui import QAction, QShortcut, QKeySequence, QMouseEvent

from src.my_constants import SETTING_NAME_OPTIONS
from src.my_types import Setting_Type
from src.controllers._controller_manager import Controller_Manager
from src.models._model_manager import Model_Manager
from src.views.utils.import_export_handler import ImportExportHandler
from src.ui.page_settings_ui import Ui_PageSettings

PROFILE_OPTION = "profile_container_dir"
IMAGE_OPTION = "image_container_dir"
LOGO_OPTION = "logo_file"
PROXY_OPTION = "proxy"

class PageSettings(QWidget, Ui_PageSettings):
    def __init__(self, controller_manager: Controller_Manager, model_manager:Model_Manager, parent = None):
        super(PageSettings, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("setting page".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.controller_manager = controller_manager
        self.model_manager = model_manager
        self.current_setting_option = ""
        self.proxy_model = self.model_manager.setting()
        self.base_model = self.proxy_model.get_source_model()
        self.import_export_handler = ImportExportHandler(self.controller_manager.setting_controller, self.setting_table)
        self.setup_data()
        self.setup_connections()
        self.setup_table()
        self.setup_shortcuts()

    def setup_data(self):
        self.setting_input.setTitle("")
        self.setting_value.setDisabled(True)
        self.setting_value.setPlaceholderText("")
        self.setting_save_btn.setDisabled(True)
        self.setting_is_selected.setDisabled(True)
        self.setting_option.clear()
        self.setting_option.addItem("--- Select setting ---")
        for key, value in SETTING_NAME_OPTIONS.items():
            self.setting_option.addItem(value, key)
    
    def setup_connections(self):
        self.setting_value.mouseDoubleClickEvent = self.open_dialog
        self.setting_option.currentIndexChanged.connect(self.on_setting_options_changed)
        self.setting_save_btn.clicked.connect(self.on_save_btn_clicked)
        self.action_import_btn.clicked.connect(self._handle_import)
        self.action_export_btn.clicked.connect(self._handle_export)
    
    def setup_shortcuts(self):
        delete_1 = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Backspace), self
        )
        delete_2 = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Delete), self)
        _import = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_I), self)
        _export = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_E), self)
        save = QShortcut(QKeySequence("Return"), self)

        # create_new.activated.connect(self._on_create_btn_clicked)
        delete_1.activated.connect(self._handle_delete)
        delete_2.activated.connect(self._handle_delete)
        _import.activated.connect(self._handle_import)
        _export.activated.connect(self._handle_export)
        save.activated.connect(self.on_save_btn_clicked)
    
    def setup_table(self):
        if not self.base_model: return
        self.setting_table.setModel(self.base_model)
        self.setting_table.setSortingEnabled(True)
        created_at_col_index = self.base_model.fieldIndex("created_at")
        if created_at_col_index != -1:
            self.base_model.sort(
                created_at_col_index,
                Qt.SortOrder.DescendingOrder,  # Sắp xếp giảm dần (mới nhất lên trên)
            )
        self.display_table_columns()
        self.setting_table.setSelectionBehavior(
            self.setting_table.SelectionBehavior.SelectRows
        )
        self.setting_table.setEditTriggers(
            self.setting_table.EditTrigger.NoEditTriggers
        )
        self.setting_table.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self.setting_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.setting_table.customContextMenuRequested.connect(
            self._set_table_context_menu
        )
    
    def display_table_columns(self):
        columns_to_display = [
            "value",
            "name",
            "is_selected",
            "created_at",
            "updated_at",
        ]

        for col in range(self.base_model.columnCount()):
            column_name = self.base_model.headerData(col, Qt.Orientation.Horizontal)
            if column_name not in columns_to_display:
                self.setting_table.setColumnHidden(col, True)
            else:
                self.setting_table.setColumnHidden(col, False)

    def get_selected_ids(self):
        selected_rows = self.setting_table.selectionModel().selectedRows()
        ids = []
        for index in selected_rows:
            id_value = self.base_model.record(index.row()).value("id")
            if id_value:
                ids.append(id_value)
        return ids
    
    def open_dialog(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_setting_option in [PROFILE_OPTION, IMAGE_OPTION]:
                dialog = QFileDialog(self, "Select Directory")
                dialog.setFileMode(QFileDialog.FileMode.Directory)
                if dialog.exec():
                    selected_dir = dialog.selectedFiles()[0]
                    self.setting_value.setText(selected_dir)
            elif self.current_setting_option in [LOGO_OPTION]:
                dialog = QFileDialog(self, "Select Image File", "", "Images (*.png)")
                dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
                if dialog.exec():
                    selected_file = dialog.selectedFiles()[0]
                    self.setting_value.setText(selected_file)
            else:
                return

    @pyqtSlot(QPoint)
    def _set_table_context_menu(self, pos: QPoint):
        proxy_index = self.setting_table.indexAt(pos)
        if not proxy_index.isValid():
            return
        global_pos = self.setting_table.mapToGlobal(pos)

        menu = QMenu(self.setting_table)

        set_is_select = QAction("Set selected", self)
        set_is_deselect = QAction("Set deselected", self)
        delete = QAction("Delete", self)
        menu.addAction(set_is_select)
        menu.addAction(set_is_deselect)
        menu.addAction(delete)
        set_is_select.triggered.connect(self._handle_set_select)
        set_is_deselect.triggered.connect(self._handle_set_deselect)
        delete.triggered.connect(self._handle_delete)
        menu.popup(global_pos)
    
    @pyqtSlot(QItemSelection, QItemSelection)
    def _on_selection_changed(
        self, selected: QItemSelection, deselected: QItemSelection
    ):
        sel_model = self.setting_table.selectionModel()
        hidden_to_deselect = []
        for proxy_index in sel_model.selectedRows():
            try:
                if self.setting_table.isRowHidden(proxy_index.row()):
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

    @pyqtSlot(int)
    def on_setting_options_changed(self, idx: int):
        if idx == 0:
            self.setting_value.setDisabled(True)
            self.setting_value.setPlaceholderText("")
            self.setting_save_btn.setDisabled(True)
            self.setting_is_selected.setDisabled(True)
            return
        else:
            self.setting_value.setDisabled(False)
            self.setting_save_btn.setDisabled(False)
            self.setting_is_selected.setDisabled(False)
            self.setting_is_selected.setChecked(True)
        self.current_setting_option = self.setting_option.currentData(Qt.ItemDataRole.UserRole)
        self.setting_input.setTitle(f"Add new {SETTING_NAME_OPTIONS.get(self.current_setting_option)}")
        self.setting_value.setPlaceholderText("Double click to select")

        if self.base_model and self.current_setting_option:
            filter_string = f"name = '{self.current_setting_option}'"
            self.base_model.setFilter(filter_string)
            self.base_model.select()
       
    @pyqtSlot()
    def on_save_btn_clicked(self):
        value = self.setting_value.text()
        if not value: return
        self.controller_manager.setting_controller.create(Setting_Type(
            id=None,
            name=self.current_setting_option,
            value=value,
            is_selected=self.setting_is_selected.isChecked(),
            created_at=None,
            updated_at=None
        ))
        self.setting_value.setText("")
        self.setting_value.setFocus()
        self.base_model.reload_db()
    
    @pyqtSlot()
    def _handle_set_select(self): 
        setting_ids = self.get_selected_ids()
        if not setting_ids:
            return
        for setting_id in setting_ids:
            self.controller_manager.setting_controller.toggle_select(setting_id, True)
        self.base_model.reload_db()

    @pyqtSlot()    
    def _handle_set_deselect(self):
        setting_ids = self.get_selected_ids()
        if not setting_ids:
            return
        for setting_id in setting_ids:
            self.controller_manager.setting_controller.toggle_select(setting_id, False)
        self.base_model.reload_db()
    @pyqtSlot()    
    def _handle_delete(self):
        setting_ids = self.get_selected_ids()
        if not setting_ids:
            return
        for setting_id in setting_ids:
            self.controller_manager.setting_controller.delete(setting_id)
        self.base_model.reload_db()
    
    @pyqtSlot()
    def _handle_import(self):
        self.import_export_handler.handleImport()
        self.base_model.reload_db()

    @pyqtSlot()
    def _handle_export(self):
        self.import_export_handler.handleExport()
        self.base_model.reload_db()