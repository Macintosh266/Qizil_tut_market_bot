from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.abstract_models import BaseModels


class ProductsModel(BaseModels):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(255), index=True)  # qidiruv uchun index
    discription: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    image_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stock: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    market: Mapped["MarketModel"] = relationship(back_populates="products")
    category: Mapped["CategoryModel"] = relationship(back_populates="products")
    order_items: Mapped[list["OrderItemModel"]] = relationship(back_populates="product")
    statistics: Mapped[list["StatisticModel"]] = relationship(back_populates="product")
