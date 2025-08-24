from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class BrandItemBase(BaseModel):
    type: str = Field(..., description="Type of the item (logo, font, colour, merch)")
    name: Optional[str] = Field(None, description="Human-readable name for the item")
    link: str = Field(..., description="URL or path to the resource")
    colour: Optional[str] = Field(None, description="Colour associated with the item (hex code)")


class BrandItemCreate(BrandItemBase):
    pass


class BrandItemRead(BrandItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BrandBookBase(BaseModel):
    name: str = Field(..., description="Name of the brand book")
    description: Optional[str] = Field(None, description="Short description of the brand book")


class BrandBookCreate(BrandBookBase):
    pass


class BrandBookRead(BrandBookBase):
    id: int
    items: List[BrandItemRead] = []

    model_config = ConfigDict(from_attributes=True)
