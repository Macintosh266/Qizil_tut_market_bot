from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.abstract_models import BaseModels


class MarketModel(BaseModels):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    address: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)
    billz_shop_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    # Har bir do'kon Billz'da o'zining ALOHIDA akkauntiga (shuning uchun
    # o'zining alohida API kalitiga) ega — shu sabab bu kalit MARKET
    # darajasida saqlanadi, botning umumiy .env sozlamasida emas.
    # Shifrlangan (Fernet) qiymat asl kalitdan uzunroq bo'lgani uchun
    # yetarli joy qoldiramiz (VARCHAR(255) ba'zi uzun kalitlar uchun
    # tor bo'lib qolishi mumkin edi).
    billz_secret_key: Mapped[str | None] = mapped_column(String(512), nullable=True)

    products: Mapped[list["ProductsModel"]] = relationship(back_populates="market")
    statistics: Mapped[list["StatisticModel"]] = relationship(back_populates="market")
    staff_members: Mapped[list["UserModel"]] = relationship(back_populates="market")
