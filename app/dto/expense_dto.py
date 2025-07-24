from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ExpenseDTO(BaseModel):
    id: Optional[int] = None
    amount: float = Field(..., gt=0)
    description: str
    date: date
    category: Optional[str] = None