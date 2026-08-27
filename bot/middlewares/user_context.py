import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

from bot.database.repository.user_repo import get_user_by_telegram_id
from bot.lexicons import get_text

logger = logging.getLogger(__name__)


class UserContextMiddleware(BaseMiddleware):
    """
    Har bir update uchun bazadagi UserModel'ni topib data["db_user"]ga qo'yadi
    (agar hali ro'yxatdan o'tmagan bo'lsa - None). data["lang"] orqali joriy
    tilni beradi (standart "uz"), hamda bloklangan foydalanuvchilarni to'xtatadi.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session = data["session"]
        tg_user: User | None = data.get("event_from_user")

        db_user = None
        if tg_user:
            db_user = await get_user_by_telegram_id(session, tg_user.id)

        data["db_user"] = db_user
        data["lang"] = db_user.language.value if db_user else "uz"

        if db_user and db_user.is_banned:
            text = get_text("banned", data["lang"])
            try:
                if isinstance(event, Message):
                    await event.answer(text)
                elif isinstance(event, CallbackQuery):
                    await event.answer(text, show_alert=True)
            except Exception:
                logger.exception("Ban xabarini yuborishda xato")
            return None

        return await handler(event, data)
