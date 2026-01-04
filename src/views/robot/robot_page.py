# src/views/robot/robot_page.py
from typing import List, Tuple, Dict, Any
from PyQt6.QtWidgets import QWidget, QMenu, QFileDialog, QLineEdit, QMessageBox, QTreeWidgetItem
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
    QPoint,
    QItemSelection,
    QItemSelectionModel,
)
from PyQt6.QtGui import QAction, QShortcut, QKeySequence, QMouseEvent

from src.my_constants import SETTING_NAME_OPTIONS, ROBOT_ACTION_OPTIONS
from src.my_types import Setting_Type
from src.controllers._controller_manager import Controller_Manager
from src.models._model_manager import Model_Manager
from src.views.utils.display_order_filter import (
    apply_display_order_filter,
    prune_hidden_selection,
)
from src.ui.page_robot_ui import Ui_PageFacebookRobot
from src.views.robot.robot_action import RobotAction
from src.views.robot.robot_run_dialog import RobotRun


class PageRobot(QWidget, Ui_PageFacebookRobot):
    status_msg = pyqtSignal(str)

    def __init__(self, controller_manager: Controller_Manager, model_manager: Model_Manager, parent=None):
        super(PageRobot, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("robot page".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.controller_manager = controller_manager
        self.model_manager = model_manager

        self.proxy_model = self.model_manager.profile()
        self.base_model = self.proxy_model.get_source_model()

        self.dict_robot_tasks: Dict[str, Any] = {}
        self.tasks = []

        self.setup_table()
        self.setup_connections()
        self.setup_filters()
        self.setup_shortcuts()

        self.results_container.setHidden(True)

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

    def setup_connections(self):
        self.action_add_btn.clicked.connect(self._on_add_action_clicked)
        self.action_save_btn.clicked.connect(self._on_save_action_clicked)
        self.action_run_btn.clicked.connect(self._on_run_action_clicked)

    def setup_filters(self):
        filter_widgets = {
            self.username_input: self.base_model.fieldIndex("username"),
            self.uid_input: self.base_model.fieldIndex("uid"),
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
                    widget.activated.connect(
                        lambda idx, w=widget: handler(w.currentText()))
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

                self.display_order_input.textChanged.connect(
                    _on_display_order_changed)
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
        reload = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_R), self)
        create_new = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_N), self)
        delete_1 = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Backspace), self
        )
        delete_2 = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Delete), self)
        save = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S), self)
        run = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Return), self)
        create_new.activated.connect(self._on_add_action_clicked)
        reload.activated.connect(
            lambda: (self.base_model.reload_db(), self._emit_current_stats())
        )
        delete_1.activated.connect(self._handle_delete_fb_action_widget)
        delete_2.activated.connect(self._handle_delete_fb_action_widget)
        save.activated.connect(self._on_save_action_clicked)
        run.activated.connect(self._on_run_action_clicked)

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
            id_value = self.base_model.data(
                id_index, Qt.ItemDataRole.DisplayRole)
            if id_value:
                selected_ids.append(id_value)
        return selected_ids

    def get_selected_uid_and_id(self):
        ids_uids_selected: List[Tuple[str, str]] = []
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
                id_value = self.base_model.data(
                    id_index, Qt.ItemDataRole.DisplayRole)
                uid_value = self.base_model.data(
                    uid_index, Qt.ItemDataRole.DisplayRole)
                if id_value is None and uid_value is None:
                    continue
                ids_uids_selected.append(
                    (str(uid_value) if uid_value is not None else "",
                     str(id_value) if id_value is not None else "")
                )
            except Exception:
                pass
        return ids_uids_selected

    def display_table_columns(self):
        columns_to_display = [
            "uid",
            "username",
            "profile_note",
            "profile_type",
            "profile_group",
            "profile_name",
            "created_at",
        ]

        for col in range(self.base_model.columnCount()):
            column_name = self.base_model.headerData(
                col, Qt.Orientation.Horizontal)
            if column_name not in columns_to_display:
                self.profiles_table.setColumnHidden(col, True)
            else:
                self.profiles_table.setColumnHidden(col, False)

    def set_actions_tree_view(self, dict_robot_tasks: Dict[str, Any]):
        self.actions_tree_view.clear()



        for profile_id, action_info in dict_robot_tasks.items():
            profile = action_info["profile"]
            profile_info = profile["info"]
            profile_path = profile["profile_path"]
            actions = action_info["actions"]
            if not actions:
                continue
            tree_account_item = QTreeWidgetItem(
                [
                    f"{profile_info.username} ({profile_info.uid})"
                ]
            )
            for action in actions:
                action_name = action["action_name"]
                tree_action_item = QTreeWidgetItem([ROBOT_ACTION_OPTIONS[action_name].capitalize()])
                tree_account_item.addChild(tree_action_item)
            self.actions_tree_view.addTopLevelItem(tree_account_item)
        self.actions_tree_view.expandAll()

# -----------------
# Slot
# -----------------

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
    def _on_add_action_clicked(self):
        action_w = RobotAction(self)
        self.action_payload_layout.addWidget(action_w)

    @pyqtSlot()
    def _handle_delete_fb_action_widget(self):
        count = self.action_payload_layout.count()
        if count > 0:
            last_widget = self.action_payload_layout.itemAt(count - 1).widget()
            if isinstance(last_widget, RobotAction):
                last_widget.setParent(None)
                last_widget.deleteLater()

    @pyqtSlot()
    def _on_save_action_clicked(self):
        robot_tasks = {}
        selected_profile_id = self.get_selected_ids()
        if not selected_profile_id:
            return

        action_widgets: List[RobotAction] = (
            self.action_payload_layout.parentWidget().findChildren(RobotAction)
        )
        actions: List[Dict[str, Any]] = []
        for idx, action_widget in enumerate(action_widgets):
            value = action_widget.get_value()
            if value == None or not value.get("action_name"):
                QMessageBox.warning(
                    self,
                    "Action Data is Empty",
                    f"Data for action number {idx + 1} has not been set.",
                    QMessageBox.StandardButton.Retry,
                    QMessageBox.StandardButton.Retry,
                )
                return
            else:
                actions.append(value)

        for profile_id in selected_profile_id:
            if actions:
                profile = self.controller_manager.profile_controller.read(
                    profile_id)
                robot_tasks[profile_id] = {
                    "profile": profile,
                    "actions": actions
                }
            else:
                if profile_id in robot_tasks:
                    del robot_tasks[profile_id]
        
        sorted_dict = dict(sorted(
            robot_tasks.items(), 
            key=lambda item: item[1]['profile']['info'].username
        ))
        self.tasks = self.controller_manager.robot_controller.init_robot_tasks(sorted_dict)
        self.set_actions_tree_view(sorted_dict)

    @pyqtSlot()
    def _on_run_action_clicked(self): 
        self.run_robot_dialog = RobotRun(self)
        self.run_robot_dialog.show()
        self.run_robot_dialog.setting_data_signal.connect(self._handle_run_robot)
    
    @pyqtSlot(dict)
    def _handle_run_robot(self, settings: Dict[str, Any]):
        self.controller_manager.robot_controller.handle_run_bot(self.tasks, settings)
        pass