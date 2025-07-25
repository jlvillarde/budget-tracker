import os
import json
from typing import List
from fastapi import HTTPException
from data.categories import default_categories


DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data/expenses')
os.makedirs(DATA_DIR, exist_ok=True)


class CategoryService:

    def _get_user_file(self, user_id: int) -> str:
        return os.path.join(DATA_DIR, f"user_{user_id}.json")

    def _initialize_user_file_if_missing(self, user_id: int):
        file_path = self._get_user_file(user_id)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"expenses": [], "categories": default_categories}, f, indent=2)

    def _read_categories(self, user_id: int) -> List[str]:
        self._initialize_user_file_if_missing(user_id)
        file_path = self._get_user_file(user_id)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("categories", [])

    def _write_categories(self, user_id: int, categories: List[str]):
        file_path = self._get_user_file(user_id)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["categories"] = categories
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def list_categories(self, user_id: int) -> List[str]:
        return self._read_categories(user_id)

    def add_category(self, user_id: int, category: str):
        categories = self._read_categories(user_id)
        if category in categories:
            raise HTTPException(status_code=400, detail="Category already exists")
        categories.append(category)
        self._write_categories(user_id, categories)

    def delete_category(self, user_id: int, category: str):
        categories = self._read_categories(user_id)
        if category not in categories:
            raise HTTPException(status_code=404, detail="Category not found")
        categories.remove(category)
        self._write_categories(user_id, categories)
