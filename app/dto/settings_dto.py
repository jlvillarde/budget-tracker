# app/schemas/settings_dto.py
from pydantic import BaseModel
from typing import Optional


class BudgetLimitsDTO(BaseModel):
    daily: float
    weekly: float
    monthly: float


class SettingsDTO(BaseModel):
    budgetLimits: BudgetLimitsDTO
