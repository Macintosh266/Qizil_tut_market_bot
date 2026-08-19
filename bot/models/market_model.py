from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.abstract_models import BaseModels


class MarketModel(BaseModels):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    address: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)

    products: Mapped[list["ProductsModel"]] = relationship(back_populates="market")
    statistics: Mapped[list["StatisticModel"]] = relationship(back_populates="market")
    staff_members: Mapped[list["UserModel"]] = relationship(back_populates="market")
