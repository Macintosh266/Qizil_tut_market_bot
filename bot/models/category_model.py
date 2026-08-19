from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.abstract_models import BaseModels


class CategoryModel(BaseModels):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )

    children: Mapped[list["CategoryModel"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Mapped["CategoryModel | None"] = relationship(
        back_populates="children", remote_side=[id]
    )
    products: Mapped[list["ProductsModel"]] = relationship(back_populates="category")
