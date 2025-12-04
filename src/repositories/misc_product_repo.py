# src/repositories/misc_product_repo.py
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import asdict
from src.my_constants import DB_TABLES
from src.repositories._base_repo import BaseRepository
from src.my_types import MiscProduct_Type


MISC_PRODUCT_TABLE = DB_TABLES["misc_product"]


class MiscProduct_Repo(BaseRepository):
    """
    Repository class for managing MiscProduct records in the database.
    """

    def _dict_to_misc_product(self, data: Dict[str, Any]) -> MiscProduct_Type:
        """Converts a database dictionary record into a MiscProduct_Type dataclass."""
        required_keys = [
            field.name for field in MiscProduct_Type.__dataclass_fields__.values()
        ]
        return MiscProduct_Type(**{key: data.get(key) for key in required_keys})

    def insert(
        self, product_payload: MiscProduct_Type
    ) -> Union[MiscProduct_Type, bool]:
        """Inserts a single MiscProduct_Type record into the database."""
        product_payload.id = self.init_id()
        product_payload.created_at = self.init_time()
        product_payload.updated_at = product_payload.created_at

        sql = f"""
        INSERT INTO {MISC_PRODUCT_TABLE} (
            id, status, name, description, created_at, updated_at
        ) VALUES (
            :id, :status, :name, :description, :created_at, :updated_at
        )
        """
        if super().insert(sql=sql, params=asdict(product_payload)):
            return product_payload
        return False

    def update_product(self, product_payload: MiscProduct_Type) -> bool:
        """Updates an existing MiscProduct_Type record based on its ID."""
        if not product_payload.id:
            self.logger.error("Attempted to update misc product without an ID.")
            return False

        product_payload.updated_at = self.init_time()

        sql = f"""
        UPDATE {MISC_PRODUCT_TABLE} SET
            status = :status,
            name = :name,
            description = :description,
            updated_at = :updated_at
        WHERE id = :id
        """
        params = asdict(product_payload)
        return super().update(sql=sql, params=params)
    
    def change_status(self, id: str, status: str) -> bool:
        sql = f"""
        UPDATE {MISC_PRODUCT_TABLE} SET
            status = :status,
            updated_at = :updated_at
        WHERE id = :id
        """
        params = {
            "id": id,
            "status": status, 
            "updated_at": self.init_time(),
        }
        return self.update(sql=sql, params=params)

    def refresh_updated_at(self, product_id: str) -> bool:
        """Refreshes the 'updated_at' timestamp for a misc product record."""
        current_time = self.init_time()
        sql = f"""
        UPDATE {MISC_PRODUCT_TABLE} SET
            updated_at = :updated_at
        WHERE id = :id
        """
        params = {"id": product_id, "updated_at": current_time}
        return super().update(sql=sql, params=params)
    
    def delete_product_by_id(self, product_id: str) -> bool:
        """Deletes a misc product record by its primary key ID."""
        sql = f"DELETE FROM {MISC_PRODUCT_TABLE} WHERE id = :id"
        return super().delete(sql=sql, params={"id": product_id})

    def get_product_by_id(self, product_id: str) -> Optional[MiscProduct_Type]:
        """Retrieves a single misc product record by its primary key ID."""
        sql = f"SELECT * FROM {MISC_PRODUCT_TABLE} WHERE id = :id"
        result_dict = super().get_one(sql=sql, params={"id": product_id})

        if result_dict:
            return self._dict_to_misc_product(result_dict)
        return None

    def get_random_product_by_name_and_update_days(
        self, name: str, days: int
    ) -> Optional[MiscProduct_Type]:
        """
        Retrieves a random MiscProduct_Type record whose name matches (name)
        and whose 'updated_at' field is older than the specified number of days (days).
        (updated_at < current time - days)
        """
        time_ago = (datetime.now() - timedelta(days=days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        sql = f"""
        SELECT * FROM {MISC_PRODUCT_TABLE}
        WHERE name = :name AND updated_at < :time_ago
        ORDER BY RANDOM() LIMIT 1
        """
        params = {"name": name, "time_ago": time_ago}
        result_dict = super().get_one(sql=sql, params=params)

        if result_dict:
            return self._dict_to_misc_product(result_dict)
        return None

    def get_all_products(self) -> List[MiscProduct_Type]:
        """Retrieves all misc product records from the table."""
        sql = f"SELECT * FROM {MISC_PRODUCT_TABLE}"
        results_list = super().get_all(sql=sql)

        return [self._dict_to_misc_product(data) for data in results_list]

    def get_all_for_export(self) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {MISC_PRODUCT_TABLE}"
        return super().get_all(sql=sql)

    def insert_bulk(self, payload: List[Any]) -> bool:
        """Inserts multiple MiscProduct_Type records in a single transaction."""
        if not payload:
            return True

        params_list = []
        for product in payload:
            product.id = self.init_id()
            product.created_at = self.init_time()
            product.updated_at = product.created_at
            params_list.append(asdict(product))

        sql = f"""
        INSERT INTO {MISC_PRODUCT_TABLE} (
            id, status, name, description, created_at, updated_at
        ) VALUES (
            :id, :status, :name, :description, :created_at, :updated_at
        )
        """

        repo_super = super(MiscProduct_Repo, self)

        def execute_bulk_insert() -> Tuple[bool, Any]:
            success = repo_super.execute_many(sql=sql, params_list=params_list)
            return success, None

        success, _ = repo_super.execute_in_transaction(execute_bulk_insert)
        return success
