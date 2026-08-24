from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.abstract_models import BaseModels


class BrandModel(BaseModels):
    """Mahsulot brendi (ishlab chiqaruvchi/savdo belgisi). Ixtiyoriy —
    mahsulotning brendi bo'lmasligi ham mumkin (brand_id nullable)."""

    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    products: Mapped[list["ProductsModel"]] = relationship(back_populates="brand")
