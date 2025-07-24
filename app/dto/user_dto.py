from pydantic import BaseModel, EmailStr, Field

class UserCreateDTO(BaseModel):
    email: EmailStr = Field(..., description="Unique email")
    password: str = Field(..., min_length=8, description="Password with at least 8 characters")
    firstname: str = Field(..., min_length=1, description="User's first name")
    lastname: str = Field(..., min_length=1, description="User's last name")
