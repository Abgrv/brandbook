from __future__ import annotations

from . import models, schemas
from typing import List, Optional
from sqlalchemy.orm import Session


def create_brandbook(db: Session, owner_id: int, brandbook: schemas.BrandBookCreate) -> models.BrandBook:
    db_obj = models.BrandBook(name=brandbook.name, description=brandbook.description, owner_id=owner_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_brandbooks(db: Session, owner_id: int) -> List[models.BrandBook]:
    return db.query(models.BrandBook).filter(models.BrandBook.owner_id == owner_id).all()


def create_item(db: Session, brandbook_id: int, item: schemas.BrandItemCreate) -> models.BrandItem:
    db_item = models.BrandItem(
        brandbook_id=brandbook_id,
        type=item.type,
        name=item.name,
        link=item.link,
        colour=item.colour,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_brandbook(db: Session, owner_id: int, brandbook_id: int) -> Optional[models.BrandBook]:
    return db.query(models.BrandBook).filter(models.BrandBook.id == brandbook_id, models.BrandBook.owner_id == owner_id).first()