import json
from typing import List
from fastapi import HTTPException
from app.utils.file_manager import initialize_user_categories_file


class CategoryService:

    def _get_user_categories_file(self, user_id: int):
        """Get the user's categories file path, creating it if it doesn't exist."""
        return initialize_user_categories_file(user_id)

    def _read_categories(self, user_id: int) -> List[str]:
        """Read categories from user's categories file."""
        file_path = self._get_user_categories_file(user_id)
        with file_path.open("r", encoding="utf-8") as f:
            categories = json.load(f)
        return categories

    def _write_categories(self, user_id: int, categories: List[str]):
        """Write categories to user's categories file."""
        file_path = self._get_user_categories_file(user_id)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)

    def list_categories(self, user_id: int) -> List[str]:
        """List all categories for the user."""
        return self._read_categories(user_id)

    def add_category(self, user_id: int, category: str) -> List[str]:
        """Add a new category and return updated list."""
        categories = self._read_categories(user_id)
        if category in categories:
            raise HTTPException(status_code=400, detail="Category already exists")
        categories.append(category)
        self._write_categories(user_id, categories)
        return categories 

    def delete_category(self, user_id: int, category: str) -> List[str]:
        """Delete a category and return updated list."""
        categories = self._read_categories(user_id)
        if category not in categories:
            raise HTTPException(status_code=404, detail="Category not found")
        categories.remove(category)
        self._write_categories(user_id, categories)
        return categories 

    def update_category(self, user_id: int, old_name: str, new_name: str):
        categories = self._read_categories(user_id)

        if old_name not in categories:
            raise HTTPException(status_code=404, detail="Original category not found")

        if new_name in categories:
            raise HTTPException(status_code=400, detail="New category name already exists")

        index = categories.index(old_name)
        categories[index] = new_name
        self._write_categories(user_id, categories)
