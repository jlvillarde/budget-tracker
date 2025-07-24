from fastapi import APIRouter, Request, Depends
from typing import List
from app.dto.expense_dto import ExpenseDTO
from app.services.expense_service import ExpenseService
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    dependencies=[Depends(get_current_user)]  # 👈 This applies to all routes in this router!
)
expense_service = ExpenseService()

@router.post("/", response_model=ExpenseDTO)
def add_expense(expense: ExpenseDTO, request: Request):
    user_id = request.session["user"]["id"]
    return expense_service.add_expense(user_id, expense)

@router.get("", response_model=List[ExpenseDTO])
def list_expenses(request: Request):
    user_id = request.session["user"]["id"]
    return expense_service.list_expenses(user_id)

@router.put("/{expense_id}", response_model=ExpenseDTO)
def update_expense(expense_id: int, expense: ExpenseDTO, request: Request):
    user_id = request.session["user"]["id"]
    return expense_service.update_expense(user_id, expense_id, expense)

@router.delete("/{expense_id}")
def delete_expense(expense_id: int, request: Request):
    user_id = request.session["user"]["id"]
    expense_service.delete_expense(user_id, expense_id)
    return {"message": "Expense deleted"}