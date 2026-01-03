from fastapi import FastAPI, Query, HTTPException, Path
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Union, Literal
from math import ceil

app = FastAPI(title='My Mini Blog')

BLOG_POST = [
    {'id': 1, 'title': 'Primera entrada', 'content': 'Primera entrada del Mini Blog'},
    {'id': 2, 'title': 'Segona entrada', 'content': 'Segona entrada del Mini Blog'},
    {'id': 3, 'title': 'Django versus FastAPI', 'content': 'FastAPI és més ràpid que Django segons la comunitat',
     'tags': [
        {'name': 'Python'},
        {'name': 'Fastapi'},
        {'name': 'Django'}
    ]},
    {'id': 4, 'title': 'Primera entrada', 'content': 'Primera entrada del Mini Blog'},
    {'id': 5, 'title': 'Segona entrada', 'content': 'Segona entrada del Mini Blog'},
    {'id': 6, 'title': 'Django versus FastAPI', 'content': 'FastAPI és més ràpid que Django segons la comunitat'},
    {'id': 7, 'title': 'Primera entrada', 'content': 'Primera entrada del Mini Blog'},
    {'id': 8, 'title': 'Segona entrada', 'content': 'Segona entrada del Mini Blog'},
    {'id': 9, 'title': 'Django versus FastAPI', 'content': 'FastAPI és més ràpid que Django segons la comunitat'},
    {'id': 10, 'title': 'Primera entrada', 'content': 'Primera entrada del Mini Blog'},
    {'id': 11, 'title': 'Segona entrada', 'content': 'Segona entrada del Mini Blog'},
    {'id': 12, 'title': 'Django versus FastAPI', 'content': 'FastAPI és més ràpid que Django segons la comunitat', 'tags': [
        {'name': 'Python'},
        {'name': 'Fastapi'},
        {'name': 'Django'}
    ]},
    {'id': 13, 'title': 'Primera entrada', 'content': 'Primera entrada del Mini Blog'},
    {'id': 14, 'title': 'Segona entrada', 'content': 'Segona entrada del Mini Blog'},
    {'id': 15, 'title': 'Django versus FastAPI', 'content': 'FastAPI és més ràpid que Django segons la comunitat'},
    {'id': 16, 'title': 'Primera entrada', 'content': 'Primera entrada del Mini Blog'},
    {'id': 17, 'title': 'Segona entrada', 'content': 'Segona entrada del Mini Blog', 'tags': [
        {'name': 'Python'},
        {'name': 'Fastapi'},
        {'name': 'Django'}
    ]},
    {'id': 18, 'title': 'Django versus FastAPI', 'content': 'FastAPI és més ràpid que Django segons la comunitat'}
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
    tags: Optional[List[Tag]] = Field(default_factory=list)
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
    tags: List[Tag] = Field(default_factory=list)
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
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None

class PostPublic(PostBase):
    id: int

class PostSummary(BaseModel):
    id: int
    title: str

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

@app.get('/')
def home():
    return {'message': 'Benvinguts al Mini Blog by Eduard Farinyes'}

@app.get('/posts', response_model=PaginatedPosts)
def list_posts(
    text: Optional[str] = Query(
        default = None,
        deprecated=True,
        description = 'Paràmetres obsolets, ara es fa servir "query" o "search"'
),
    query: Optional[str] = Query(
        default = None,
        description = 'Buscar per títol',
        alias='search',
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáàéàíïóòúÁÀÉÈÍÏÓÒÚüÜ-]+$"
),

    per_page:int = Query(
        10, ge=1, le=50,
        description='Resultat de la cerca(1-50)'
    ),
    page:int = Query(
        1, ge=1,
        description='Número de pàgina (>=1)'
    ),
    order_by: Literal['id', 'title'] = Query(
        'id', description='Camp ordenació'
    ),
    direction: Literal['desc', 'asc'] = Query(
        'asc', description='Ordenació ascendent'
    )
):
    results = BLOG_POST
    query = query or text
    if query:
        results = [post for post in results if query.lower() in post['title'].lower()] # list compression
    total = len(results)
    total_pages = ceil(total / per_page) if total > 0 else 0

    if total_pages == 0:
        current_page = 1
    else:
        current_page = min(page, total_pages)

    results = sorted(results, key=lambda post: post[order_by], reverse=(direction == 'desc'))

    if total_pages == 0:
        items = []
    else:
        start = (current_page - 1) * per_page
        items = results[start:start + per_page]

    has_prev = current_page > 1
    has_next = current_page < total_pages if total > 0 else False

    return PaginatedPosts(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )

@app.get('/posts/by-tags', response_model=List[PostPublic])
def filter_posts_by_tags(
        tags: List[str] = Query(
            ...,
            min_length=2,
            description='Filter por tags. Example: ?tags=python&tags=fastapi'
        )
):
    tags_lower = [tag.lower() for tag in tags]

    return [
        post for post in BLOG_POST if any( tag['name'].lower() in tags_lower for tag in post.get('tags', []))
    ]


@app.get('/posts/{post_id}', response_model=Union[PostPublic, PostSummary], response_description='Entrada trobada')
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title='ID del post',
    description='Identificador del Post. Ha de ser més gran de 1',
    example= 1
), include_content: bool = Query(default = True, description = 'Incloure o no el contingut')):
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










