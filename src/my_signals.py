# src/my_signals.py
from PyQt6.QtCore import QObject, pyqtSignal

class DB_Signal(QObject):
    info = pyqtSignal(str)
    failed = pyqtSignal(str)
    error = pyqtSignal(str)
    warning = pyqtSignal(str)