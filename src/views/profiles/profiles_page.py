# src/views/profiles/profiles_page.py
from typing import  Any, Dict, List, Tuple
from PyQt6.QtWidgets import QWidget, QLineEdit, QMenu, QMessageBox
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
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

from src.my_constants import LAUNCH
from src.views.profiles.create_new_profile_dialog import CreateNewProfileDialog
from src.views.profiles.update_existed_profile_dialog import UpdateExistedProfileDialog
from src.views.utils.import_export_handler import ImportExportHandler

PROFILE_LIVE = "live"
PROFILE_DEAD = "dead"

from src.ui.page_profiles_ui import Ui_PageProfiles

class PageProfiles(QWidget, Ui_PageProfiles):
    status_msg = pyqtSignal(str)
    def __init__(self, controller_manager: Controller_Manager, model_manager: Model_Manager, parent = None):
        super(PageProfiles, self).__init__(parent=None)
        self.setupUi(self)
        self.setWindowTitle("facebook account page".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.controller_manager = controller_manager
        self.model_manager = model_manager
        self.proxy_model = self.model_manager.profile()
        self.base_model = self.proxy_model.get_source_model()
        self.import_export_handler = ImportExportHandler(self.controller_manager.profile_controller, self.profiles_table)

        self.setup_table()
        self.setup_connections()
        self.setup_filters()
        self.setup_shortcuts()

    
    def setup_table(self):
        self.profiles_table.setModel(self.proxy_model)
        self.profiles_table.setSortingEnabled(True)
        created_at_col_index = self.base_model.fieldIndex("created_at")
        if created_at_col_index != -1:
            self.base_model.sort(
                created_at_col_index,
                Qt.SortOrder.DescendingOrder,
            )
        self.display_table_columns()
        self.profiles_table.setSelectionBehavior(
            self.profiles_table.SelectionBehavior.SelectRows
        )
        self.profiles_table.setEditTriggers(
            self.profiles_table.EditTrigger.NoEditTriggers
        )
        self.profiles_table.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self.profiles_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.profiles_table.customContextMenuRequested.connect(
            self._set_table_context_menu
        )
    
    def setup_connections(self):
        self.action_create_btn.clicked.connect(self._on_create_btn_clicked)
        self.action_import_btn.clicked.connect(self._handle_import)
        self.action_export_btn.clicked.connect(self._handle_export)

    def setup_filters(self):
        filter_widgets = {
            self.two_fa_input: self.base_model.fieldIndex("two_fa"),
            self.email_input: self.base_model.fieldIndex("email"),
            self.username_input: self.base_model.fieldIndex("username"),
            self.uid_input: self.base_model.fieldIndex("uid"),
            self.phone_number_input: self.base_model.fieldIndex("phone_number"),
            self.note_input: self.base_model.fieldIndex("account_note"),
            self.type_input: self.base_model.fieldIndex("account_type"),
            self.group_input: self.base_model.fieldIndex("account_group"),
            self.name_input: self.base_model.fieldIndex("account_name"),
        }
        for widget, col_index in filter_widgets.items():
            if col_index is None or col_index == -1:
                continue

            def make_handler(c_idx):
                def _on_text_changed(text: str):
                    try:
                        self.proxy_model.set_filter_column(c_idx)
                        self.proxy_model.filter_by_text(text)
                        prune_hidden_selection(self.profiles_table)
                    except Exception:
                        pass

                return _on_text_changed

            handler = make_handler(col_index)

            try:
                if hasattr(widget, "textChanged"):
                    widget.textChanged.connect(handler)
                elif hasattr(widget, "currentTextChanged"):
                    widget.currentTextChanged.connect(handler)
                elif hasattr(widget, "activated"):
                    widget.activated.connect(lambda idx, w=widget: handler(w.currentText()))
            except Exception:
                pass

        if hasattr(self, "display_order_input"):
            try:
                def _on_display_order_changed(text: str):
                    try:
                        apply_display_order_filter(self.profiles_table, text)
                        prune_hidden_selection(self.profiles_table)
                    except Exception:
                        pass

                self.display_order_input.textChanged.connect(_on_display_order_changed)
            except Exception:
                pass
        try:
            if hasattr(self, "filter_input") and isinstance(
                self.filter_input, QLineEdit
            ):
                self.filter_input.textChanged.connect(
                    lambda text: apply_display_order_filter(
                        self.profiles_table, text
                    )
                )
        except Exception:
            pass

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
                self.profiles_table.setColumnHidden(col, True)
            else:
                self.profiles_table.setColumnHidden(col, False)
    
    def get_selected_ids(self):
        selected_rows_indexes = (
            self.profiles_table.selectionModel().selectedRows()
        )
        selected_ids = []
        id_col = self.base_model.fieldIndex("id")
        if id_col == -1:
            return []
        for proxy_index in selected_rows_indexes:
            if self.profiles_table.isRowHidden(proxy_index.row()):
                continue
            source_index = self.proxy_model.mapToSource(proxy_index)
            id_index = self.base_model.index(source_index.row(), id_col)
            id_value = self.base_model.data(id_index, Qt.ItemDataRole.DisplayRole)
            if id_value:
                selected_ids.append(id_value)
        return selected_ids
    
    def get_selected_uid_and_id(self):
        ids_uids_selected:List[Tuple[str, str]] = []
        id_col = self.base_model.fieldIndex("id")
        uid_col = self.base_model.fieldIndex("uid")
        if id_col == -1 or uid_col == -1:
            return ids_uids_selected

        for proxy_index in self.profiles_table.selectionModel().selectedRows():
            try:
                if self.profiles_table.isRowHidden(proxy_index.row()):
                    continue
                source_index = self.proxy_model.mapToSource(proxy_index)
                id_index = self.base_model.index(source_index.row(), id_col)
                uid_index = self.base_model.index(source_index.row(), uid_col)
                id_value = self.base_model.data(id_index, Qt.ItemDataRole.DisplayRole)
                uid_value = self.base_model.data(uid_index, Qt.ItemDataRole.DisplayRole)
                if id_value is None and uid_value is None:
                    continue
                ids_uids_selected.append(
                    (str(uid_value) if uid_value is not None else "", str(id_value) if id_value is not None else "")
                )
            except Exception:
                pass
        return ids_uids_selected
    
    @pyqtSlot(QPoint)
    def _set_table_context_menu(self, pos: QPoint):
        proxy_index = self.profiles_table.indexAt(pos)
        if not proxy_index.isValid():
            return
        global_pos = self.profiles_table.mapToGlobal(pos)

        menu = QMenu(self.profiles_table)
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
        sel_model = self.profiles_table.selectionModel()
        hidden_to_deselect = []
        for proxy_index in sel_model.selectedRows():
            try:
                if self.profiles_table.isRowHidden(proxy_index.row()):
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
        currently_selected_rows_indexes = self.profiles_table.selectionModel().selectedRows()
        selected_row_keys = set()
        for index in currently_selected_rows_indexes:
            row_number = index.row()
            selected_row_keys.add(row_number)

        self.status_msg.emit(f"Selected: {len(selected_row_keys)}")
        
    
    @pyqtSlot()
    def _on_launch_as_desktop(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids: return
        profiles = [self.controller_manager.profile_controller.read(_) for _ in selected_ids]
        payload = []
        for profile in profiles:
            payload.append({"profile": profile, "action_payload": {"mobile_mode": False, "action_name": LAUNCH}})
        self.controller_manager.robot_controller.handle_facebook_action(
            payload,
            {},
        )

    @pyqtSlot()    
    def _on_launch_as_mobile(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids: return
        profiles = [self.controller_manager.profile_controller.read(_) for _ in selected_ids]
        payload = []
        for profile in profiles:
            payload.append({"profile": profile, "action_payload": {"mobile_mode": True, "action_name": LAUNCH}})
        self.controller_manager.robot_controller.handle_facebook_action(
            payload,
            {}, # setting
        )

    @pyqtSlot()    
    def _on_check_live(self):
        uid_id_selected = self.get_selected_uid_and_id()
        if not uid_id_selected: return
        self.controller_manager.robot_controller.handle_check_live(uid_id_selected)
        self.base_model.reload_db()

    @pyqtSlot()    
    def _on_change_to_live(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids: return

        for selected_id in selected_ids:
            self.controller_manager.profile_controller.change_status(selected_id, PROFILE_LIVE)
        self.base_model.reload_db()

    @pyqtSlot()    
    def _on_change_to_dead(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids: return
        for selected_id in selected_ids:
            self.controller_manager.profile_controller.change_status(selected_id, PROFILE_DEAD)
        self.base_model.reload_db()

    @pyqtSlot()    
    def _on_update(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids: return
        prev_data = self.controller_manager.profile_controller.read(selected_ids[0])
        self.update_existed_profile = UpdateExistedProfileDialog(prev_data.get("info"), self)
        self.update_existed_profile.show()
        self.update_existed_profile.profile_data_signal.connect(self._handle_update_existed_profile)

    @pyqtSlot()    
    def _on_delete(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids: return
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {len(selected_ids)} profiles?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.No:
            return
        else:
            for selected_id in selected_ids:
                self.controller_manager.profile_controller.delete(selected_id)
        self.base_model.reload_db()

    @pyqtSlot()
    def _on_create_btn_clicked(self):
        self.create_new_profile = CreateNewProfileDialog(self)
        self.create_new_profile.show()
        self.create_new_profile.profile_data_signal.connect(
            self._handle_create_new_profile
        )
    
    @pyqtSlot(dict)
    def _handle_create_new_profile(self, data: Dict[str, Any]):
        self.controller_manager.profile_controller.create(data)
        self.base_model.reload_db()
    
    @pyqtSlot(dict)
    def _handle_update_existed_profile(self, data:Dict[str, Any]):
        self.controller_manager.profile_controller.update(data.get("id"), data)
        self.base_model.reload_db()

    @pyqtSlot()
    def _handle_import(self):
        self.import_export_handler.handleImport()
        self.base_model.reload_db()

    @pyqtSlot()
    def _handle_export(self):
        self.import_export_handler.handleExport()
        self.base_model.reload_db()