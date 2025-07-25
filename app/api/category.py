from fastapi import APIRouter, Request, Depends, status
from typing import List
from app.services.category_service import CategoryService
from app.dependencies.auth import get_current_user
from app.dto.category_dto import CategoryDTO

router = APIRouter(
    tags=["categories"],
    dependencies=[Depends(get_current_user)]
)

category_service = CategoryService()

@router.get("/categories", response_model=List[str])
def list_categories(request: Request):
    user_id = request.session["user"]["id"]
    return category_service.list_categories(user_id)

@router.post("/categories", status_code=status.HTTP_201_CREATED)
def add_category(category: CategoryDTO, request: Request):
    user_id = request.session["user"]["id"]
    category_service.add_category(user_id, category.name)
    return {"message": "Category added"}

@router.delete("/categories", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category: CategoryDTO, request: Request):
    user_id = request.session["user"]["id"]
    category_service.delete_category(user_id, category.name)
    return
