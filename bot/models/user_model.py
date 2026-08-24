from sqlalchemy import BigInteger, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.enums.enum import Language, UserRole
from bot.models.abstract_models import BaseModels


class UserModel(BaseModels):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    language: Mapped[Language] = mapped_column(
        SAEnum(Language), default=Language.UZ, nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.USER, nullable=False
    )
    # Faqat ADMIN/STAFF rolidagi foydalanuvchilar uchun to'ldiriladi — ular
    # qaysi do'konga tegishli ekanini bildiradi. SUPER_ADMIN uchun bo'sh
    # qoladi (u barcha do'konlarga kirish huquqiga ega).
    market_id: Mapped[int | None] = mapped_column(ForeignKey("markets.id"), nullable=True)
    is_alive: Mapped[bool] = mapped_column(default=True)   # profil "faol" belgisi
    is_banned: Mapped[bool] = mapped_column(default=False)

    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[list["OrderModel"]] = relationship(back_populates="user")
    feedbacks: Mapped[list["FeedbackModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    handled_statistics: Mapped[list["StatisticModel"]] = relationship(
        back_populates="staff"
    )
    market: Mapped["MarketModel | None"] = relationship(back_populates="staff_members")


class Address(BaseModels):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    address: Mapped[str] = mapped_column(String(500))
    # Xaritadan yuborilgan bo'lsa koordinatalar ham saqlanadi (ixtiyoriy —
    # matn orqali qo'lda kiritilgan manzillarda bo'sh qoladi)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)  # xaridorning joriy manzili

    user: Mapped["UserModel"] = relationship(back_populates="addresses")
