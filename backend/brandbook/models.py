from backend.users.models import Base
from backend.users.models import Brandbook
from typing import Optional
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship


class BrandItem(Base):
    """An item within a brand book (logo, font, colour, merch)."""

    __tablename__ = "brand_items"

    id: int = Column(Integer, primary_key=True, index=True)
    brandbook_id: int = Column(Integer, ForeignKey("brandbooks.id"), nullable=False)
    type: str = Column(String, nullable=False)  # e.g. "logo", "font", "colour", "merch"
    name: Optional[str] = Column(String, nullable=True)
    link: str = Column(String, nullable=False)
    colour: Optional[str] = Column(String, nullable=True)

    brandbook = relationship(Brandbook, back_populates="items")