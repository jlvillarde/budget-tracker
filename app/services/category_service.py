import json
from typing import List
from fastapi import HTTPException
from app.services.storage.storage_factory import storage_factory

class CategoryService:

    def __init__(self):
        self.storage = storage_factory()

    def _read_categories(self, user_id: int) -> List[str]:
        """Read expenses for a user from the configured storage."""
        categories = self.storage.load_file(user_id, 'catrgories')
        return categories if isinstance(categories, list) else [categories]

    def _write_categories(self, user_id: int, categories: list):
        """Save category into categories file"""
        return self.storage.save_file(user_id, 'categories', categories)


    def list_categories(self, user_id: int) -> List[str]:
        """List all categories for the user."""
        categories =  self._read_categories(user_id)

        default_categories = [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Personal Care",
        ]

        if len(categories) == 0:
            self._write_categories(user_id, default_categories)
            return default_categories
        
        else:
            return categories

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
