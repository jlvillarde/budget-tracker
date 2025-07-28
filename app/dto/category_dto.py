from pydantic import BaseModel, Field

class CategoryDTO(BaseModel):
    name: str = Field(..., description="The name of the category")


class UpdateCategoryDTO(BaseModel):
    old_name: str = Field(..., description="The current name of the category")
    new_name: str = Field(..., description="The new name of the category")