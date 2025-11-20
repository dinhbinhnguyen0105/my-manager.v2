# src/database/qt_database.py

from PyQt6.QtSql import QSqlDatabase
from src.utils.logger import Logger


class QtDatabase:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QtDatabase, cls).__new__(cls)
            cls._instance.logger = Logger(cls.__name__)
            cls._instance._db = QSqlDatabase.addDatabase("QSQLITE")
            cls._instance._db.setDatabaseName(cls.db_path)

        return cls._instance

    def connect(self) -> bool:
        if not self._db.isOpen():
            if self._db.open():
                self.logger.info("Database connection succeeded.")
                return True
            else:
                self.logger.error(
                    f"Database connection failed: {self._db.lastError().text()}."
                )
                return False
        return True

    def get_db(self) -> QSqlDatabase:
        if self._db and self._db.isOpen():
            return self._db
        self.logger.error("Database connection is not available.")
        raise ConnectionError("Database connection is not open.")

    def close_connection(self):
        if self._db and self._db.isOpen():
            self._db.close()
            self.logger.info("Database connection has been closed.")

    def is_connected(self) -> bool:
        return self._db and self._db.isOpen()

    def get_error(self):
        if self._db:
            return self._db.lastError()
        return None

    def __del__(self):
        self.close_connection()
