from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from . import crud, schemas
from sqlalchemy.orm import Session

from database import get_db
from backend.users.dependencies import current_user  # adjust import as needed


router = APIRouter(prefix="/brandbooks", tags=["brandbooks"])


@router.post("/", response_model=schemas.BrandBookRead, status_code=status.HTTP_201_CREATED)
def api_create_brandbook(
    brandbook: schemas.BrandBookCreate,
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
    """Create a new brand book belonging to the authenticated user."""
    return crud.create_brandbook(db, owner_id=current_user.id, brandbook=brandbook)


@router.get("/", response_model=List[schemas.BrandBookRead])
def api_list_brandbooks(
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
    """List all brand books belonging to the authenticated user."""
    return crud.get_brandbooks(db, owner_id=current_user.id)


@router.get("/{brandbook_id}", response_model=schemas.BrandBookRead)
def api_get_brandbook(
    brandbook_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
    """Retrieve a single brand book by ID."""
    brandbook = crud.get_brandbook(db, owner_id=current_user.id, brandbook_id=brandbook_id)
    if not brandbook:
        raise HTTPException(status_code=404, detail="BrandBook not found")
    return brandbook


@router.post("/{brandbook_id}/items", response_model=schemas.BrandItemRead, status_code=status.HTTP_201_CREATED)
def api_add_item(
    brandbook_id: int,
    item: schemas.BrandItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(current_user),
):
    """Add an item (logo, font, colour, merch) to a specific brand book."""
    brandbook = crud.get_brandbook(db, owner_id=current_user.id, brandbook_id=brandbook_id)
    if not brandbook:
        raise HTTPException(status_code=404, detail="BrandBook not found")
    return crud.create_item(db, brandbook_id=brandbook_id, item=item)