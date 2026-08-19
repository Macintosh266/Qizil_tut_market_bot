from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from bot.enums.enum import UserRole
from bot.models import UserModel


class IsAdmin(BaseFilter):
    """Do'kon admini VA super-admin (super-admin barcha admin buyruqlariga ham ega)."""

    async def __call__(self, event: TelegramObject, db_user: UserModel | None = None) -> bool:
        return bool(db_user and db_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN))


class IsSuperAdmin(BaseFilter):
    """Faqat platforma darajasidagi super-admin — do'kon yaratish, do'konga admin
    tayinlash kabi barcha do'konlarga tegishli amallar uchun."""

    async def __call__(self, event: TelegramObject, db_user: UserModel | None = None) -> bool:
        return bool(db_user and db_user.role == UserRole.SUPER_ADMIN)


class IsStaff(BaseFilter):
    """Ishchi, do'kon admini VA super-admin (barchasi ishchi buyruqlariga ega)."""

    async def __call__(self, event: TelegramObject, db_user: UserModel | None = None) -> bool:
        return bool(
            db_user and db_user.role in (UserRole.STAFF, UserRole.ADMIN, UserRole.SUPER_ADMIN)
        )
