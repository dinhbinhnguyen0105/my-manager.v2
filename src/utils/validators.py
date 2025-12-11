# src/utils/validator.py
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator


class FloatValidator(QRegularExpressionValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        regex = QRegularExpression(r"^\d*(?:.?\d*)?$")
        self.setRegularExpression(regex)