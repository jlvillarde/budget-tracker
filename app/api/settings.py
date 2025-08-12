from typing import Annotated
from fastapi import APIRouter, Request, Depends
from app.dto.settings_dto import BudgetLimitsDTO, SettingsDTO
from app.services.settings_service import SettingsService
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    dependencies=[Depends(get_current_user)]
)
SettingsServiceDep = Annotated[SettingsService, Depends(SettingsService)]

@router.get("")
def get_settings(
    request: Request,
    settings_service: SettingsServiceDep
):
    user_id = request.session["user"]["id"]
    return settings_service.get_user_settings(user_id)

@router.put("")
def update_settings(
    dto: BudgetLimitsDTO,
    request: Request,
    settings_service: SettingsServiceDep
):
    user_id = request.session["user"]["id"]
    return settings_service.update_user_settings(user_id, dto.dict())
