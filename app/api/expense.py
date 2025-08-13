from enum import StrEnum
from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile
from typing import Annotated, List
from app.dto.expense_dto import ExpenseDTO
from app.services.expense_service import ExpenseService
from app.dependencies.auth import get_current_user
from app.services.file_transfer.file_transfer_factory import FileType, file_transfer_factory

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

@router.get("/export/{user_id}")
def export_expenses(
    user_id: int,
    file_type: FileType
):
    file_transfer = file_transfer_factory(file_type)
    return file_transfer.export_file(user_id)

@router.post('/import/{user_id}')
def import_expenses(
    user_id: int,
    import_file: UploadFile
):
    """
    Import expenses from CSV or JSON file.
    
    Args:
        user_id: The user ID to import expenses for
        import_file: The uploaded file (CSV or JSON)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If file type is unsupported or import fails
    """
    try:
        # Primary check: content type
        if import_file.content_type in ['text/csv', 'application/csv']:
            file_type = FileType.CSV
        elif import_file.content_type in ['application/json', 'text/json']:
            file_type = FileType.JSON
        else:
            # Fallback: check file extension if content type is unreliable
            if import_file.filename:
                filename_lower = import_file.filename.lower()
                if filename_lower.endswith('.csv'):
                    file_type = FileType.CSV
                elif filename_lower.endswith('.json'):
                    file_type = FileType.JSON
                else:
                    raise HTTPException(
                        status_code=400, 
                        detail="Unsupported file type. Only CSV and JSON files are allowed."
                    )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Unable to determine file type. Please ensure the file has a proper extension."
                )
        
        # Import the file using the factory pattern
        file_transfer_factory(file_type).import_file(user_id, import_file)
        
        return {
            "message": "File imported successfully",
            "file_type": file_type.value
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while importing the file: {str(e)}"
        )
