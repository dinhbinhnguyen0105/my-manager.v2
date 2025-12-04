# src/repositories/property_template_repo.py

from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import asdict
from src.my_constants import DB_TABLES
from src.repositories._base_repo import BaseRepository
from src.my_types import PropertyTemplate_Type


PROPERTY_TEMPLATE_TABLE = DB_TABLES["property_template"]


class PropertyTemplate_Repo(BaseRepository):
    """
    Repository class for managing PropertyTemplate records in the database.
    """

    def _dict_to_property_template(self, data: Dict[str, Any]) -> PropertyTemplate_Type:
        """Converts a database dictionary record into a PropertyTemplate_Type dataclass."""
        required_keys = [
            field.name for field in PropertyTemplate_Type.__dataclass_fields__.values()
        ]
        # Handle the field name difference: 'name' (in DB SQL) corresponds to 'part' (in dataclass)
        # Note: The SQL schema uses 'name', but the Python dataclass uses 'part'.
        # We must align them during conversion.
        data["part"] = data.pop("name")
        return PropertyTemplate_Type(**{key: data.get(key) for key in required_keys})

    def insert(
        self, template_payload: PropertyTemplate_Type
    ) -> Union[PropertyTemplate_Type, bool]:
        """Inserts a single PropertyTemplate_Type record into the database."""
        template_payload.id = self.init_id()
        template_payload.created_at = self.init_time()
        template_payload.updated_at = (
            template_payload.created_at
        )  # Assuming updated_at field is also needed for consistency

        # Use temporary dict for mapping dataclass 'part' back to DB 'name'
        params = asdict(template_payload)
        params["name"] = params.pop("part")

        sql = f"""
        INSERT INTO {PROPERTY_TEMPLATE_TABLE} (
            id, transaction_type, name, category, value, is_default, created_at, updated_at
        ) VALUES (
            :id, :transaction_type, :name, :category, :value, :is_default, :created_at, :updated_at
        )
        """
        if super().insert(sql=sql, params=params):
            return template_payload
        return False

    def update_template(self, template_payload: PropertyTemplate_Type) -> bool:
        """Updates an existing PropertyTemplate_Type record based on its ID."""
        if not template_payload.id:
            self.logger.error("Attempted to update property template without an ID.")
            return False

        template_payload.updated_at = self.init_time()

        params = asdict(template_payload)
        params["name"] = params.pop("part")

        sql = f"""
        UPDATE {PROPERTY_TEMPLATE_TABLE} SET
            transaction_type = :transaction_type,
            name = :name,
            category = :category,
            value = :value,
            is_default = :is_default,
            updated_at = :updated_at
        WHERE id = :id
        """
        return super().update(sql=sql, params=params)
    
    def change_status(self, id: str, status: str) -> bool:
        sql = f"""
        UPDATE {PROPERTY_TEMPLATE_TABLE} SET
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

    def delete_template_by_id(self, template_id: str) -> bool:
        """Deletes a property template record by its primary key ID."""
        sql = f"DELETE FROM {PROPERTY_TEMPLATE_TABLE} WHERE id = :id"
        return super().delete(sql=sql, params={"id": template_id})

    def get_template_by_id(self, template_id: str) -> Optional[PropertyTemplate_Type]:
        """Retrieves a single property template record by its primary key ID."""
        sql = f"SELECT * FROM {PROPERTY_TEMPLATE_TABLE} WHERE id = :id"
        result_dict = super().get_one(sql=sql, params={"id": template_id})

        if result_dict:
            return self._dict_to_property_template(result_dict)
        return None
    def get_all_for_export(self) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {PROPERTY_TEMPLATE_TABLE}"
        return super().get_all(sql=sql)
    def get_all_templates(self) -> List[PropertyTemplate_Type]:
        """Retrieves all property template records from the table."""
        sql = f"SELECT * FROM {PROPERTY_TEMPLATE_TABLE}"
        results_list = super().get_all(sql=sql)

        return [self._dict_to_property_template(data) for data in results_list]

    def get_random_template_by_filters(
        self,
        transaction_type: str,
        name: str,
        category: str,
        is_default: bool = True,
    ) -> Optional[PropertyTemplate_Type]:
        """
        Retrieves a random PropertyTemplate_Type record matching the specified filters.
        Filters include transaction_type, name (which is 'part' in the dataclass),
        category, and optionally is_default.
        """
        is_default_int = 1 if is_default else 0
        sql = f"""
        SELECT * FROM {PROPERTY_TEMPLATE_TABLE}
        WHERE transaction_type = :transaction_type
          AND name = :name
          AND category = :category
          AND is_default = :is_default
        ORDER BY RANDOM()
        LIMIT 1
        """
        params = {
            "transaction_type": transaction_type,
            "name": name,
            "category": category,
            "is_default": is_default_int,
        }

        result_dict = super().get_one(sql=sql, params=params)

        if result_dict:
            return self._dict_to_property_template(result_dict)
        return None
    
    def insert_bulk(self, payload: List[Any]) -> bool:
        """Inserts multiple PropertyProduct_Type records in a single transaction."""
        if not payload:
            return True

        params_list = []
        for product in payload:
            product.id = self.init_id()
            product.created_at = self.init_time()
            product.updated_at = product.created_at
            params_list.append(asdict(product))

        sql = f"""
        INSERT INTO {PROPERTY_TEMPLATE_TABLE} (
            id, transaction_type, name, category, value, is_default, created_at, updated_at
        ) VALUES (
            :id, :transaction_type, :name, :category, :value, :is_default, :created_at, :updated_at
        )
        """

        repo_super = super(PropertyTemplate_Repo, self)

        def execute_bulk_insert() -> Tuple[bool, Any]:
            success = repo_super.execute_many(sql=sql, params_list=params_list)
            return success, None

        success, _ = repo_super.execute_in_transaction(execute_bulk_insert)
        return success