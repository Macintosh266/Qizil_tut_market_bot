from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.engine import Base


class BaseModels(Base):
    """Barcha modellar uchun umumiy abstrakt asos: create_data / update_data."""

    __abstract__ = True

    create_data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    update_data: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
