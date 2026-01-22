from typing import Optional, List, Union, Literal, Annotated
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from fastapi import Form

class Tag(BaseModel):
    name: str = Field(..., min_length=3, max_length=20, description='Nom de l\'etiqueta')
    model_config = ConfigDict(from_attributes=True)

class Author(BaseModel):
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    title: str
    content: str
    # tags: Optional[List[Tag]] = []
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None
    image_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description='Títol del post (mínim 3 caràcters i màxim 100)',
        examples= ['El meu primer post amb FastApi'],
    )
    content: Optional[str] = Field(
        default= 'Contingut per defecte, modificable posteriorment',
        min_length = 10,
        description= 'Contingut del post (mínim 10 caràcters)',
        examples= ['El meu primer post amb FastApi. És vàlid perquè te més de 10 caràcters'],
    )
    tags: List[Tag] = Field(default_factory=list)
    # author: Optional[Author] = None

    @field_validator('title')
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        forbidden_words = ['spam', 'publicitat', 'comerç', 'html','sql', 'test']
        for word in forbidden_words:
            if word in value.lower():
                print(word)
                raise ValueError(f'Error. {word} no es paraula permesa')
        return value
    @classmethod
    def as_form(
            cls,
            title: Annotated[str, Form(min_length=5)],
            content: Annotated[str, Form(min_length=10)],
            tags: Annotated[Optional[list[str]], Form()] = None,
    ):
        tag_objs = [Tag(name=tag) for tag in (tags or [])]
        return cls(title=title, content=content, tags=tag_objs)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None

class PostPublic(PostBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PostSummary(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)

class PaginatedPosts(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal['id', 'title']
    direction: Literal['desc', 'asc']
    search: Optional[str] = None
    items: List[PostPublic]
