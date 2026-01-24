from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.tags.schemas import TagPublic, TagCreate
from app.core.db import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post('', response_model=TagPublic, response_description='Etiqueta creada', status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    from app.api.v1.tags.repository import TagRepository
    repository = TagRepository(db)

    try:
        tag_created = repository.create_tag(name=tag.name)
        db.commit()
        db.refresh(tag_created)
        return tag_created
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail='Error al crear l\'etiqueta')