# src/repositories/setting_repo.py

from typing import Dict, Tuple, Any, Optional, List, Union
from dataclasses import asdict
from src.my_constants import DB_TABLES
from src.repositories._base_repo import BaseRepository
from src.my_types import Setting_Type


SETTING_TABLE = DB_TABLES["setting"]
SETTING_PROXY_OPTION = "proxy"


class Setting_Repo(BaseRepository):
    """
    Repository class for managing Setting records in the database.
    """

    def _dict_to_setting(self, data: Dict[str, Any]) -> Setting_Type:
        """Converts a database dictionary record into a Setting_Type dataclass."""
        required_keys = [
            field.name for field in Setting_Type.__dataclass_fields__.values()
        ]
        return Setting_Type(**{key: data.get(key) for key in required_keys})

    def insert(self, setting_payload: Setting_Type) -> Union[Setting_Type, bool]:
        """Inserts a single Setting_Type record into the database."""
        setting_payload.id = self.init_id()
        setting_payload.created_at = self.init_time()
        setting_payload.updated_at = (
            setting_payload.created_at
        )  # Add updated_at for consistency

        sql = f"""
        INSERT INTO {SETTING_TABLE} (
            id, name, value, is_selected, created_at, updated_at
        ) VALUES (
            :id, :name, :value, :is_selected, :created_at, :updated_at
        )
        """
        if super().insert(sql=sql, params=asdict(setting_payload)):
            return setting_payload
        return False

    def update_setting(self, setting_payload: Setting_Type) -> bool:
        """Updates an existing Setting_Type record based on its ID."""
        if not setting_payload.id:
            self.logger.error("Attempted to update setting without an ID.")
            return False

        setting_payload.updated_at = self.init_time()

        sql = f"""
        UPDATE {SETTING_TABLE} SET
            name = :name,
            value = :value,
            is_selected = :is_selected,
            updated_at = :updated_at
        WHERE id = :id
        """
        params = asdict(setting_payload)
        return super().update(sql=sql, params=params)

    def update_setting_by_name(
        self, setting_name: str, new_value: str, new_is_selected: bool = False
    ) -> bool:
        """Updates the value and is_selected for a setting based on its name."""
        updated_at = self.init_time()
        sql = f"""
        UPDATE {SETTING_TABLE} SET
            value = :value,
            is_selected = :is_selected,
            updated_at = :updated_at
        WHERE name = :name
        """
        params = {
            "name": setting_name,
            "value": new_value,
            "is_selected": new_is_selected,
            "updated_at": updated_at,
        }
        return super().update(sql=sql, params=params)

    def delete_setting_by_id(self, setting_id: str) -> bool:
        """Deletes a setting record by its primary key ID."""
        sql = f"DELETE FROM {SETTING_TABLE} WHERE id = :id"
        return super().delete(sql=sql, params={"id": setting_id})

    def get_setting_by_id(self, setting_id: str) -> Optional[Setting_Type]:
        """Retrieves a single setting record by its primary key ID."""
        sql = f"SELECT * FROM {SETTING_TABLE} WHERE id = :id"
        result_dict = super().get_one(sql=sql, params={"id": setting_id})

        if result_dict:
            return self._dict_to_setting(result_dict)
        return None

    def get_setting_by_name(self, setting_name: str) -> Optional[Setting_Type]:
        """Retrieves a single setting record by its unique name."""
        sql = f"SELECT * FROM {SETTING_TABLE} WHERE name = :name"
        result_dict = super().get_one(sql=sql, params={"name": setting_name})

        if result_dict:
            return self._dict_to_setting(result_dict)
        return None

    def get_setting_value_by_name(self, setting_name: str) -> Optional[str]:
        setting = self.get_setting_by_name(setting_name)
        if not setting:
            return None
        else:
            return setting.value
    
    def get_proxies_selected(self) -> List[str]:
        sql = f"SELECT * FROM {SETTING_TABLE} WHERE name = :name AND is_selected = :is_selected"
        params = {
            "name": SETTING_PROXY_OPTION,
            "is_selected": True
        }
        result_list = super().get_all(sql, params)
        for _ in result_list:
            _.get("value")
        return [_.get("value") for _ in result_list]
    
    def toggle_select(self, setting_id: str, is_selected: bool) -> bool:
        sql = f"""
        UPDATE {SETTING_TABLE} SET
            is_selected = :is_selected,
            updated_at = :updated_at
        WHERE id = :id
        """
        params = {
            "id": setting_id,
            "is_selected": 1 if is_selected else 0, 
            "updated_at": self.init_time(),
        }
        return self.update(sql=sql, params=params)
    
    def get_all_for_export(self) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {SETTING_TABLE}"
        return super().get_all(sql=sql)
    def get_all_settings(self) -> List[Setting_Type]:
        """Retrieves all setting records from the table."""
        sql = f"SELECT * FROM {SETTING_TABLE}"
        results_list = super().get_all(sql=sql)

        return [self._dict_to_setting(data) for data in results_list]

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
        INSERT INTO {SETTING_TABLE} (
            id, name, value, is_selected, created_at, updated_at
        ) VALUES (
            :id, :name, :value, :is_selected, :created_at, :updated_at
        )
        """

        repo_super = super(Setting_Repo, self)

        def execute_bulk_insert() -> Tuple[bool, Any]:
            success = repo_super.execute_many(sql=sql, params_list=params_list)
            return success, None

        success, _ = repo_super.execute_in_transaction(execute_bulk_insert)
        return success