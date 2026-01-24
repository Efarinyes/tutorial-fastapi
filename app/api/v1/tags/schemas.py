from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TagPublic(BaseModel):
    id: int
    name: str = Field(..., min_length=4, max_length=35, description='Nom de l\'etiqueta')
    model_config = ConfigDict(from_attributes=True)

class TagCreate(BaseModel):
    name: str = Field(..., min_length=4, max_length=35, description='Nom de l\'etiqueta')

class TagUpdate(BaseModel):
    name: str = Field(..., min_length=4, max_length=35, description='Nom de l\'etiqueta')

class TagWithCount(TagUpdate):
    uses: int