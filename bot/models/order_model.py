from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.enums.enum import DeliveryType, OrderStatus
from bot.models.abstract_models import BaseModels


class OrderModel(BaseModels):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus), default=OrderStatus.NEW
    )
    delivery_type: Mapped[DeliveryType] = mapped_column(SAEnum(DeliveryType))
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)  # faqat DELIVERY uchun
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    phone: Mapped[str] = mapped_column(String(32))
    total_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    user: Mapped["UserModel"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    statistics: Mapped[list["StatisticModel"]] = relationship(back_populates="order")


class OrderItemModel(BaseModels):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(default=1)
    price: Mapped[float] = mapped_column(Numeric(12, 2))  # buyurtma paytidagi narx

    order: Mapped["OrderModel"] = relationship(back_populates="items")
    product: Mapped["ProductsModel"] = relationship(back_populates="order_items")
    statistic: Mapped["StatisticModel"] = relationship(back_populates="order_item")
