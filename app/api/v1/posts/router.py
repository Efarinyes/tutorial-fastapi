from fastapi import APIRouter, Query, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional, Union, Literal
from math import ceil
from app.core.db import get_db
from .schemas import (PostPublic, PostSummary, PaginatedPosts, PostCreate, PostUpdate)
from .repository import PostRepository

router = APIRouter(prefix="/posts", tags=['posts'])

@router.get('', response_model=PaginatedPosts)
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
    repository = PostRepository(db)
    query = query or text
    total, items = repository.search(query, order_by, page, direction, per_page)
    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

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
@router.get('/by_tags', response_model=List[PostPublic])
def filter_posts_by_tags(tags: List[str] = Query(
            ..., min_length=1, description='Filter por tags. Example: ?tags=python&tags=fastapi'), db: Session = Depends(get_db)
):
    repository = PostRepository(db)
    return repository.by_tags(tags)

@router.get('/{post_id}', response_model=Union[PostPublic, PostSummary], response_description='Entrada trobada')
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title='ID del post',
    description='Identificador del Post. Ha de ser més gran de 1',
    examples= [1]
), include_content: bool = Query(default = True, description = 'Incloure o no el contingut'), db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail='Entrada no trobada')
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)
    return PostSummary.model_validate(post, from_attributes=True)


@router.post('', response_model=PostPublic, response_description='Entrada creada correctament',
          status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    repository = PostRepository(db)

    try:
        post = repository.create_post(
            title=post.title,
            content=post.content,
            author = (post.author.model_dump() if post.author else None),
            tags = [tag.model_dump() for tag in post.tags]
        )
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Títol ja existeix')
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail='Error al crear post')


@router.put('/{post_id}',
            response_model=PostPublic,
            response_description='Entrada creada correctament',
            response_model_exclude_none=True)

def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail='Entrada no existeix')
    try:
        updates = data.model_dump(exclude_none=True)
        post = repository.update_post(post, updates)
        db.commit()
        db.refresh(post)
        return post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail='Error al actualitzar el post')

@router.delete('/{post_id}',status_code=status.HTTP_204_NO_CONTENT   )
def delete_post(post_id: int, db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail='Entrada no existeix')

    try:
        repository.delete_post(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail='Error al eliminar el post')

