# src/views/utils/display_order_filter.py
import re
from typing import Optional, Tuple
from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtWidgets import QTableView

# Regex used by both pages
_MODULO_RE = re.compile(r"^(?P<op>==|!=|>=|<=|>|<)?(?P<mod>%?)(?P<num>\d+)$")


def parse_filter_expr(text: str) -> Optional[Tuple[str, str, int]]:
    """Parse a filter expression like '==%3', '!=%2', '%2', '==5'.

    Returns (op, mode, n) where mode is 'mod' or 'cmp', or None if invalid.
    """
    if not text:
        return None
    s = text.strip()
    m = _MODULO_RE.match(s)
    if not m:
        return None
    op = m.group("op") or "=="
    mode = "mod" if m.group("mod") == "%" else "cmp"
    try:
        n = int(m.group("num"))
    except Exception:
        return None
    if n == 0:
        return None
    return op, mode, n


def _eval_index_filter(op: str, mode: str, n: int, stt: int) -> bool:
    """Evaluate parsed filter for a 1-based stt. Return True to SHOW row."""
    if mode == "mod":
        lhs = stt % n
        if op == "==":
            return lhs == 0
        if op == "!=":
            return lhs != 0
        if op == ">":
            return lhs > 0
        if op == "<":
            return lhs < 0
        if op == ">=":
            return lhs >= 0
        if op == "<=":
            return lhs <= 0
        return False
    else:
        if op == "==":
            return stt == n
        if op == "!=":
            return stt != n
        if op == ">":
            return stt > n
        if op == "<":
            return stt < n
        if op == ">=":
            return stt >= n
        if op == "<=":
            return stt <= n
        return False


def apply_display_order_filter(table_view: QTableView, text: str) -> None:
    """Apply display-order filter expression to a QTableView.

    This function operates on the model currently set on the view (proxy model),
    so row indexes are in view/proxy space (reflect current sorting).
    It hides rows that do not satisfy the expression using `setRowHidden`.
    """
    parsed = parse_filter_expr(text)
    model = table_view.model()
    if model is None:
        return
    row_count = model.rowCount()

    if parsed is None:
        # show all
        for r in range(row_count):
            table_view.setRowHidden(r, False)
        return

    op, mode, n = parsed
    for proxy_row in range(row_count):
        stt = proxy_row + 1
        keep = _eval_index_filter(op, mode, n, stt)
        table_view.setRowHidden(proxy_row, not keep)


def prune_hidden_selection(table_view: QTableView) -> None:
    """Deselect any selected rows that are currently hidden in the view.

    Use this after selection changes (or before acting on selection) to ensure
    hidden rows are not mistakenly treated as selected.
    """
    sel_model = table_view.selectionModel()
    if sel_model is None:
        return
    to_deselect = []
    for proxy_index in sel_model.selectedRows():
        try:
            if table_view.isRowHidden(proxy_index.row()):
                to_deselect.append(proxy_index)
        except Exception:
            # ignore any error checking row visibility
            pass

    if not to_deselect:
        return

    for idx in to_deselect:
        sel_model.select(
            idx,
            QItemSelectionModel.SelectionFlag.Deselect
            | QItemSelectionModel.SelectionFlag.Rows,
        )
