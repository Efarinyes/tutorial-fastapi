from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Union

app = FastAPI(title='My Mini Blog')

BLOG_POST = [
    {'id': 1, 'title': 'Primera entrada', 'content': 'Primera entrada del Mini Blog'},
    {'id': 2, 'title': 'Segona entrada', 'content': 'Segona entrada del Mini Blog'},
    {'id': 3, 'title': 'Django versus FastAPI', 'content': 'FastAPI és més ràpid que Django segons la comunitat'}
]

class Tag(BaseModel):
    name: str = Field(..., min_length=3, max_length=20, description='Nom de l\'etiqueta')

class Author(BaseModel):
    name: str
    email: EmailStr

class PostBase(BaseModel):
    title: str
    content: str
    # tags: Optional[List[Tag]] = []
    tags: List[Tag] = []
    author: Optional[Author] = None

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
    tags: List[Tag] = []
    author: Optional[Author] = None

    @field_validator('title')
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        forbidden_words = ['spam', 'publicitat', 'comerç', 'html','sql', 'test']
        for word in forbidden_words:
            if word in value.lower():
                print(word)
                raise ValueError(f'Error. {word} no es paraula permesa')
        return value

class PostUpdate(BaseModel):
    title: str
    content: Optional[str] = None

class PostPublic(PostBase):
    id: int

class PostSummary(BaseModel):
    id: int
    title: str

@app.get('/')
def home():
    return {'message': 'Benvinguts al Mini Blog by Eduard Farinyes'}

@app.get('/posts', response_model=List[PostPublic])
def list_posts(query: str | None = Query(default = None, description = 'Buscar per títol')):
    if query:
        return [post for post in BLOG_POST if query.lower() in post['title'].lower()] # list compression
    return BLOG_POST

@app.get('/posts/{post_id}', response_model=Union[PostPublic, PostSummary], response_description='Entrada trobada')
def get_post(post_id: int, include_content: bool = Query(default = True, description = 'Incloure o no el contingut')):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not include_content:
                return {'id': post['id'], 'title': post['title']}
            return post
    return HTTPException(status_code=404, detail='Entrada inexistent')


@app.post('/posts', response_model=PostPublic, response_description='Entrada creada correctament')
def create_post(post: PostCreate):

    new_id = (BLOG_POST[-1]['id'] + 1) if BLOG_POST else 1
    new_post = {
        'id': new_id,
        'title': post.title,
        'content': post.content,
        'tags': [tag.model_dump() for tag in post.tags],
        'author': post.author.model_dump() if post.author else None
    }
    BLOG_POST.append(new_post)
    return new_post

@app.put('/posts/{post_id}',
         response_model=PostPublic,
         response_description='Entrada modificada correctament',
         response_model_exclude_none=True,
         )
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post['id'] == post_id:
            playload = data.model_dump(exclude_unset=True)
            if 'title' in playload: post['title'] = playload['title']
            if 'content' in playload: post['content'] = playload['content']
            return post

    raise HTTPException(status_code=404, detail='Entrada inexistent')

@app.delete('/posts/{post_id}', status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post['id'] == post_id:
            BLOG_POST.pop(index)
            return
    raise HTTPException(status_code=404, detail='Entrada inexistent')










