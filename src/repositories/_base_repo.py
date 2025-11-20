# src/repositories/_base_repo.py
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime
import uuid

from src.utils.logger import LoggerSingleton


class BaseRepository:

    def __init__(self, db: QSqlDatabase):
        self.db = db
        self.logger = LoggerSingleton(self.__class__.__name__)

    # --- Utility Methods ---

    def _execute_query(
        self, query: QSqlQuery, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Prepares and executes a single QSqlQuery.

        Args:
            query: The QSqlQuery object to use.
            sql: The SQL statement.
            params: Optional dictionary of parameters to bind.

        Returns:
            True if execution is successful, False otherwise.
        """
        query.prepare(sql)
        if params:
            # QtSql requires parameters to have the prefix ':'
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        if not query.exec():
            self.logger.error(f"Query error: {query.lastError().text()}")
            self.logger.error(f"SQL: {sql}")
            # IMPORTANT: Do not log full params if data is sensitive
            self.logger.error(
                f"Parameters (Partial Keys): {list(params.keys()) if params else 'None'}"
            )
            return False
        return True

    def _record_to_dict(self, record: QSqlRecord) -> Dict[str, Any]:
        """Converts a QSqlRecord object to a standard Python dictionary."""
        data = {}
        for i in range(record.count()):
            key = record.fieldName(i)
            value = record.value(i)
            # Note: For complex Qt types, further conversion might be needed here
            data[key] = value
        return data

    def init_id(self) -> str:
        """Generates a unique identifier (UUID)."""
        return str(uuid.uuid4())

    def init_time(self) -> str:
        """Generates the current timestamp in standard DB format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- CRUD Basic Methods ---

    def is_exists(self, sql: str, params: Dict[str, Any]) -> bool:
        """Checks if a record exists based on the given SQL and parameters."""
        query = QSqlQuery(self.db)
        self._execute_query(query=query, sql=sql, params=params)
        return query.next()

    def insert(self, sql: str, params: Dict[str, Any]) -> bool:
        """Executes an INSERT statement."""
        query = QSqlQuery(self.db)
        return self._execute_query(query, sql, params)

    def update(self, sql: str, params: Dict[str, Any]) -> bool:
        """Executes an UPDATE statement."""
        query = QSqlQuery(self.db)
        return self._execute_query(query, sql, params)

    def delete(self, sql: str, params: Dict[str, Any]) -> bool:
        """Executes a DELETE statement."""
        query = QSqlQuery(self.db)
        return self._execute_query(query, sql, params)

    def get_one(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a single record based on the SQL query."""
        query = QSqlQuery(self.db)
        if not self._execute_query(query, sql, params):
            return None

        if query.next():
            return self._record_to_dict(query.record())
        return None

    def get_all(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves all records matching the SQL query."""
        query = QSqlQuery(self.db)
        if not self._execute_query(query, sql, params):
            return []

        results = []
        while query.next():
            results.append(self._record_to_dict(query.record()))
        return results

    # --- Bulk/Transaction Methods ---

    def execute_many(self, sql: str, params_list: List[Dict[str, Any]]) -> bool:
        """
        Executes a single SQL statement multiple times.
        It assumes an existing transaction is open OR will run without transaction control.
        """
        if not params_list:
            return True

        query = QSqlQuery(self.db)
        # Prepare the query once outside the inner loop
        query.prepare(sql)

        for params in params_list:
            # Bind parameters for each execution
            for key, value in params.items():
                query.bindValue(f":{key}", value)

            if not query.exec():
                self.logger.error(f"Bulk execution error: {query.lastError().text()}")
                self.logger.error(f"SQL: {sql}")
                # Khi thất bại, không cần rollback ở đây, mà để execute_in_transaction xử lý.
                return False

        return True

    # --- Transaction Control Methods ---

    def start_transaction(self) -> bool:
        """Begins a database transaction."""

        return self.db.transaction()

    def commit_transaction(self) -> bool:
        """Commits the current database transaction."""
        return self.db.commit()

    def rollback_transaction(self) -> bool:
        """Rolls back the current database transaction."""
        return self.db.rollback()

    # --- Transaction Wrapper ---

    def execute_in_transaction(
        self, callback: Callable[[], Tuple[bool, Any]]
    ) -> Tuple[bool, Any]:
        """
        Executes a series of database operations provided by a callback function within a single transaction.

        Args:
            callback: A function that performs database operations and returns a tuple (success: bool, result: Any).

        Returns:
            A tuple (success: bool, result: Any) indicating the outcome of the transaction.
        """
        # CRITICAL: Check if a transaction is already active before starting a new one.
        # This check depends on the specific driver/DB behavior. If the DB automatically
        # handles nested transactions or you are sure your application manages them externally,
        # you might skip the transaction wrapper here or change its behavior.

        # We assume the caller must explicitly start the transaction via this method.
        if not self.start_transaction():
            # Log the full error from the database object
            self.logger.error(
                f"Failed to begin database transaction. Error: {self.db.lastError().text()}"
            )
            # If the database is already in a transaction, the operation should fail gracefully.
            return False, None

        try:
            success, result = callback()

            if success:
                if self.commit_transaction():
                    return True, result
                else:
                    self.logger.error(
                        f"Failed to commit database transaction. Error: {self.db.lastError().text()}"
                    )
                    self.rollback_transaction()
                    return False, None
            else:
                self.logger.warning(
                    "Callback operation reported failure. Rolling back transaction."
                )
                self.rollback_transaction()
                return False, result

        except Exception as e:
            self.logger.error(
                f"Exception occurred during transaction: {e}. Rolling back."
            )
            self.rollback_transaction()
            return False, None
