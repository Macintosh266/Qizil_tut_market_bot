from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.abstract_models import BaseModels


class FeedbackModel(BaseModels):
    """Foydalanuvchilarning bot/do'kon haqidagi fikr-mulohazalari (savol,
    taklif, shikoyat va h.k.). Admin panel orqali ko'rib chiqiladi."""

    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    is_reviewed: Mapped[bool] = mapped_column(default=False)  # admin ko'rib chiqdimi

    user: Mapped["UserModel"] = relationship(back_populates="feedbacks")
