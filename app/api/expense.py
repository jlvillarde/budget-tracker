from fastapi import APIRouter, Request, Depends
from typing import Annotated, List
from app.dto.expense_dto import ExpenseDTO
from app.services.expense_service import ExpenseService
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    dependencies=[Depends(get_current_user)]
)
ExpenseServiceDep = Annotated[ExpenseService, Depends(ExpenseService)]

@router.post("/", response_model=ExpenseDTO)
def add_expense(\
    expense: ExpenseDTO,
    expense_service: ExpenseServiceDep,
    request: Request
):
    user_id = request.session["user"]["id"]
    return expense_service.add_expense(user_id, expense)

@router.get("", response_model=List[ExpenseDTO])
def list_expenses(
    expense_service: ExpenseServiceDep,
    request: Request
):
    user_id = request.session["user"]["id"]
    return expense_service.list_expenses(user_id)

@router.put("/{expense_id}", response_model=ExpenseDTO)
def update_expense(
    expense_id: int, 
    expense: ExpenseDTO,
    expense_service: ExpenseServiceDep,
    request: Request
):
    user_id = request.session["user"]["id"]
    return expense_service.update_expense(user_id, expense_id, expense)

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    expense_service: ExpenseServiceDep,
    request: Request
):
    user_id = request.session["user"]["id"]
    expense_service.delete_expense(user_id, expense_id)
    return {"message": "Expense deleted"}