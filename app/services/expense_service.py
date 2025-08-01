import json
import datetime
from typing import List
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.dto.expense_dto import ExpenseDTO
from app.utils.file_manager import initialize_user_expenses_file
from app.utils.expense_limit_checker import ExpenseLimitChecker


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle date objects."""
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)


class ExpenseService:

    def _read_expenses(self, user_id: int) -> List[dict]:
        """Read expenses from user's expenses file."""
        file_path = initialize_user_expenses_file(user_id)
        with file_path.open("r", encoding="utf-8") as f:
            expenses = json.load(f)
        return expenses

    def _write_expenses(self, user_id: int, expenses: List[dict]):
        """Write expenses to user's expenses file."""
        file_path = initialize_user_expenses_file(user_id)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(expenses, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

    def add_expense(self, user_id: int, expense: ExpenseDTO):
        """Add a new expense for the user."""
        expenses = self._read_expenses(user_id)
        expense_id = (max([e["id"] for e in expenses], default=0) + 1) if expenses else 1
        expense.id = expense_id

        # Calculate totals for today, week, and month
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        total_today = sum(e["amount"] for e in expenses if "date" in e and datetime.date.fromisoformat(e["date"]) == today)
        total_week = sum(e["amount"] for e in expenses if "date" in e and week_start <= datetime.date.fromisoformat(e["date"]) <= today)
        total_month = sum(e["amount"] for e in expenses if "date" in e and month_start <= datetime.date.fromisoformat(e["date"]) <= today)
        # Add the new expense amount to the totals
        total_today += expense.amount
        total_week += expense.amount
        total_month += expense.amount
        # Check limits and notify if needed
        checker = ExpenseLimitChecker(user_id)
        exceeded = checker.check_and_notify(total_today, total_week, total_month)

        # Convert to dict using Pydantic's method
        try:
            expense_dict = expense.model_dump()
        except AttributeError:
            expense_dict = expense.dict()

        # Convert date fields to ISO string if needed
        if "date" in expense_dict and isinstance(expense_dict["date"], (datetime.date, datetime.datetime)):
            expense_dict["date"] = expense_dict["date"].isoformat()

        expenses.append(expense_dict)
        self._write_expenses(user_id, expenses)

        # Return JSON with info if limit exceeded
        if exceeded:
            return JSONResponse(
                status_code=201,
                content={
                    "expense": expense_dict,
                    "limit_exceeded": True,
                    "details": exceeded  # This is a list of dicts with title, detail, date
                }
            )
        return expense

    def list_expenses(self, user_id: int) -> List[ExpenseDTO]:
        """List all expenses for the user."""
        expenses = self._read_expenses(user_id)
        return [ExpenseDTO(**e) for e in expenses]

    def update_expense(self, user_id: int, expense_id: int, expense: ExpenseDTO) -> ExpenseDTO:
        """Update an existing expense for the user."""
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
        """Delete an expense for the user."""
        expenses = self._read_expenses(user_id)
        new_expenses = [e for e in expenses if e["id"] != expense_id]
        if len(new_expenses) == len(expenses):
            raise HTTPException(status_code=404, detail="Expense not found")
        self._write_expenses(user_id, new_expenses)