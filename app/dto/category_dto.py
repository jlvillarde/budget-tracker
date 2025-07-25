from pydantic import BaseModel, Field

class CategoryDTO(BaseModel):
    name: str = Field(..., description="The name of the category")
