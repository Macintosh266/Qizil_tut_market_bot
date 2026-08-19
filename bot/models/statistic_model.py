from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.enums.enum import DeliveryType
from bot.models.abstract_models import BaseModels


class StatisticModel(BaseModels):
    """Har bir sotilgan mahsulot uchun alohida log yozuvi (istalgan davr statistikasi uchun)."""

    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"), unique=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    staff_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    quantity: Mapped[int]
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    total_price: Mapped[float] = mapped_column(Numeric(12, 2))

    delivery_type: Mapped[DeliveryType] = mapped_column(SAEnum(DeliveryType))
    sold_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    order: Mapped["OrderModel"] = relationship(back_populates="statistics")
    order_item: Mapped["OrderItemModel"] = relationship(back_populates="statistic")
    market: Mapped["MarketModel"] = relationship(back_populates="statistics")
    product: Mapped["ProductsModel"] = relationship(back_populates="statistics")
    staff: Mapped["UserModel | None"] = relationship(back_populates="handled_statistics")
