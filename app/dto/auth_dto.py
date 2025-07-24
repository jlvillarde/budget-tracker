from pydantic import BaseModel, EmailStr, Field

class LoginDTO(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=6, description="User's password")
