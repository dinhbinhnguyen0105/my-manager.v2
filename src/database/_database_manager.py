# src/database/database_manager.py
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from src.database.qt_database import QtDatabase
from src.utils.logger import Logger
from src.database.sql_commands import CREATE_TABLE_SQL


class DatabaseManager:
    def __init__(self):
        self.db_instance = QtDatabase()
        if not self.db_instance.connect():
            raise ConnectionError("Could not connect to the database.")

        self.db = self.db_instance.get_db()
        self.logger = Logger(self.__class__.__name__)
        self._init_tables()

    def _init_tables(self):
        query = QSqlQuery(self.db)
        for sql in CREATE_TABLE_SQL.strip().split(";"):
            sql = sql.strip()
            if not sql:
                continue
            if not query.exec(sql):
                self.logger.error(f"Error creating tables: {query.lastError().text()}.")
        else:
            self.logger.info("All tables have been created or already exist.")

    def get_db(self) -> QSqlDatabase:
        return self.db_instance.get_db()
