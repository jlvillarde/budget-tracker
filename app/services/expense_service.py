import os
import json
import datetime
from typing import List, Optional
from fastapi import HTTPException
from app.dto.expense_dto import ExpenseDTO
from data.categories import default_categories


DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data/expenses')
os.makedirs(DATA_DIR, exist_ok=True)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle date objects."""
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

class ExpenseService:

    def initialize_user_file_if_missing(self, user_id: int):
        file_path = self._get_user_file(user_id)
        if not os.path.exists(file_path):
            initial_data = {
                "expenses": [],
                "categories": default_categories
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)


    def _get_user_file(self, user_id: int) -> str:
        return os.path.join(DATA_DIR, f"user_{user_id}.json")

    def _read_expenses(self, user_id: int) -> List[dict]:
        self.initialize_user_file_if_missing(user_id)  # Ensures the file exists
        file_path = self._get_user_file(user_id)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("expenses", [])

    def _write_expenses(self, user_id: int, expenses: List[dict]):
        file_path = self._get_user_file(user_id)
        
        # Ensure file exists
        self.initialize_user_file_if_missing(user_id)

        # Load existing content
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Update only expenses
        data["expenses"] = expenses

        # Save back
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

    def add_expense(self, user_id: int, expense: ExpenseDTO) -> ExpenseDTO:
        expenses = self._read_expenses(user_id)
        expense_id = (max([e["id"] for e in expenses], default=0) + 1) if expenses else 1
        expense.id = expense_id
        
        
        # Convert to dict using Pydantic's method
        try:
            # Try Pydantic v2 first
            expense_dict = expense.model_dump()
        except AttributeError:
            # Fallback to Pydantic v1
            expense_dict = expense.dict()
                
        expenses.append(expense_dict)
        self._write_expenses(user_id, expenses)
        return expense

    def list_expenses(self, user_id: int) -> List[ExpenseDTO]:
        expenses = self._read_expenses(user_id)
        return [ExpenseDTO(**e) for e in expenses]

    def update_expense(self, user_id: int, expense_id: int, expense: ExpenseDTO) -> ExpenseDTO:
        expenses = self._read_expenses(user_id)
        for idx, e in enumerate(expenses):
            if e["id"] == expense_id:
                expense.id = expense_id
                try:
                    expense_dict = expense.model_dump()
                except AttributeError:
                    expense_dict = expense.dict()
                expenses[idx] = expense_dict
                self._write_expenses(user_id, expenses)
                return expense
        raise HTTPException(status_code=404, detail="Expense not found")

    def delete_expense(self, user_id: int, expense_id: int):
        expenses = self._read_expenses(user_id)
        new_expenses = [e for e in expenses if e["id"] != expense_id]
        if len(new_expenses) == len(expenses):
            raise HTTPException(status_code=404, detail="Expense not found")
        self._write_expenses(user_id, new_expenses)

# Alternative: Test your ExpenseDTO directly
if __name__ == "__main__":
    from datetime import date
    
    # Test the ExpenseDTO serialization
    test_expense = ExpenseDTO(
        amount=25.50,
        description="Test expense",
        date=date.today(),
        category="Test"
    )
    
 
    # Test serialization
    try:
        serialized = test_expense.model_dump()
    except AttributeError:
        serialized = test_expense.dict()
       
    # Test JSON serialization
    try:
        json_str = json.dumps(serialized)
    except TypeError as e:
        json_str = json.dumps(serialized, cls=DateTimeEncoder)