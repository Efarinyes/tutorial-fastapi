import os
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException, Path, status, Depends
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Union, Literal
from math import ceil
from sqlalchemy import create_engine, Integer, String, Text, DateTime, select, func, UniqueConstraint, ForeignKey, \
    Table, Column
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column, relationship, selectinload, joinedload
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
# print('Connectat a : ', DATABASE_URL)

engine_kwargs = {}
if DATABASE_URL.startswith('sqlite'):
    engine_kwargs['connect_args'] = {'check_same_thread': False}
engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

class Base(DeclarativeBase):
    pass

post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class AuthorORM(Base):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Relacions
    posts: Mapped[List['PostORM']] = relationship(back_populates='author')

class TagORM(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    posts: Mapped[List['PostORM']] = relationship(
        secondary=post_tags,
        back_populates='tags',
        lazy='selectin',
    )

class PostORM(Base):
    __tablename__ = 'posts'
    __table_args__ = (UniqueConstraint('title', name='unique_post_title'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey('authors.id'))
    author: Mapped[AuthorORM] = relationship(back_populates='posts')
    tags: Mapped[List[TagORM]] = relationship(
        secondary=post_tags,
        back_populates='posts',
        lazy='selectin',
        passive_deletes=True
    )

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title='My Mini Blog')

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
    ),
    db: Session = Depends(get_db),
):
    results = select(PostORM)
    query = query or text
    if query:
        results = results.where(PostORM.title.like(f'%{query}%'))
    total = db.scalar(select(func.count()).select_from(results.subquery())) or 0
    total_pages = ceil(total / per_page) if total > 0 else 0

    current_page = 1 if total_pages == 0 else min(page, total_pages)

    if order_by == 'id':
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)
    results = results.order_by(order_col.asc() if direction == 'asc' else order_col.desc())

    # results = sorted(results, key=lambda post: post[order_by], reverse=(direction == 'desc'))

    if total_pages == 0:
        items = List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        items = db.execute(results.limit(per_page).offset(start)).scalars().all()

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
            min_length=1,
            description='Filter por tags. Example: ?tags=python&tags=fastapi'
        ),
        db: Session = Depends(get_db)
):
    normalized_tag_names = [ tag.strip().lower() for tag in tags if tag.strip()]
    if not normalized_tag_names:
        return []
    post_list = (
        select(PostORM)
        .options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author)
        ).where(PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tag_names)))
        .order_by(PostORM.id.asc())
    )
    posts = db.execute(post_list).scalars().all()

    return posts



@app.get('/posts/{post_id}', response_model=Union[PostPublic, PostSummary], response_description='Entrada trobada')
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title='ID del post',
    description='Identificador del Post. Ha de ser més gran de 1',
    examples= [1]
), include_content: bool = Query(default = True, description = 'Incloure o no el contingut'), db: Session = Depends(get_db)):
    post_find = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(post_find).scalar_one_or_none()
    # post = db.get(PostORM, post_id)
    if not post:
        raise HTTPException(status_code=404, detail='Entrada no trobada')
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)
    return PostSummary.model_validate(post, from_attributes=True)


@app.post('/posts', response_model=PostPublic, response_description='Entrada creada correctament',
          status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    author_obj = None
    if post.author:
        author_obj = db.execute(
            select(AuthorORM).where(AuthorORM.email == post.author.email)
        ).scalar_one_or_none()
        if not author_obj:
            author_obj = AuthorORM(name=post.author.name, email=post.author.email)
            db.add(author_obj)
            db.flush()


    new_post = PostORM(title=post.title, content= post.content, author=author_obj)
    for tag in post.tags:
        tag_obj = db.execute(
            select(TagORM).where(TagORM.name.ilike(tag.name))
        ).scalar_one_or_none()
        if not tag_obj:
            tag_obj = TagORM(name=tag.name)
            db.add(tag_obj)
            db.flush()
        new_post.tags.append(tag_obj)
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Títol ja existeix')
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail='Error al crear post')

@app.put('/posts/{post_id}',
         response_model=PostPublic,
         response_description='Entrada modificada correctament',
         response_model_exclude_none=True,
         )
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail='Entrada no existeix')
    update = data.model_dump(exclude_none=True)
    for key, value in update.items():
        setattr(post, key, value)

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

@app.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)
    if not post:
        raise HTTPException(status_code=404, detail='Entrada no existeix')
    db.delete(post)
    db.commit()
    return










