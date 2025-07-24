import os
import json
import datetime
from typing import List, Optional
from fastapi import HTTPException
from app.dto.expense_dto import ExpenseDTO

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
    def _get_user_file(self, user_id: int) -> str:
        return os.path.join(DATA_DIR, f"user_{user_id}.json")

    def _read_expenses(self, user_id: int) -> List[dict]:
        file_path = self._get_user_file(user_id)
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_expenses(self, user_id: int, expenses: List[dict]):
        file_path = self._get_user_file(user_id)
        with open(file_path, "w", encoding="utf-8") as f:
            # Use DateTimeEncoder as fallback
            json.dump(expenses, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

    def add_expense(self, user_id: int, expense: ExpenseDTO) -> ExpenseDTO:
        expenses = self._read_expenses(user_id)
        expense_id = (max([e["id"] for e in expenses], default=0) + 1) if expenses else 1
        expense.id = expense_id
        
        # DEBUG: Print what we're trying to serialize
        print(f"DEBUG: Expense object: {expense}")
        print(f"DEBUG: Expense type: {type(expense)}")
        print(f"DEBUG: Expense.date: {expense.date}")
        print(f"DEBUG: Expense.date type: {type(expense.date)}")
        
        # Convert to dict using Pydantic's method
        try:
            # Try Pydantic v2 first
            expense_dict = expense.model_dump()
            print(f"DEBUG: model_dump() result: {expense_dict}")
        except AttributeError:
            # Fallback to Pydantic v1
            expense_dict = expense.dict()
            print(f"DEBUG: dict() result: {expense_dict}")
        
        print(f"DEBUG: expense_dict['date'] type: {type(expense_dict['date'])}")
        
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
    
    print(f"ExpenseDTO: {test_expense}")
    print(f"Date field: {test_expense.date} (type: {type(test_expense.date)})")
    
    # Test serialization
    try:
        serialized = test_expense.model_dump()
        print(f"model_dump(): {serialized}")
        print(f"Date in dict: {serialized['date']} (type: {type(serialized['date'])})")
    except AttributeError:
        serialized = test_expense.dict()
        print(f"dict(): {serialized}")
        print(f"Date in dict: {serialized['date']} (type: {type(serialized['date'])})")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(serialized)
        print(f"JSON serialization successful: {json_str}")
    except TypeError as e:
        print(f"JSON serialization failed: {e}")
        # Try with custom encoder
        json_str = json.dumps(serialized, cls=DateTimeEncoder)
        print(f"JSON with custom encoder: {json_str}")