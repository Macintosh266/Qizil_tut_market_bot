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

        # DEBUG: tg_user umuman topilyaptimi
        logger.info("UserContextMiddleware: tg_user=%s", tg_user.id if tg_user else None)

        db_user = None
        if tg_user:
            db_user = await get_user_by_telegram_id(session, tg_user.id)

        # DEBUG: db_user va uning is_banned qiymati
        logger.info(
            "UserContextMiddleware: db_user=%s is_banned=%s",
            db_user.telegram_id if db_user else None,
            db_user.is_banned if db_user else None,
        )

        data["db_user"] = db_user
        data["lang"] = db_user.language.value if db_user else "uz"

        if db_user and db_user.is_banned:
            logger.info("UserContextMiddleware: BAN aniqlandi, xabar yuborishga urinilmoqda")
            text = get_text("banned", data["lang"])
            try:
                if isinstance(event, Message):
                    await event.answer(text)
                elif isinstance(event, CallbackQuery):
                    await event.answer(text, show_alert=True)
                logger.info("UserContextMiddleware: ban xabari muvaffaqiyatli yuborildi")
            except Exception:
                # Xatoni endi YASHIRMAYMIZ — to'liq traceback konsolga chiqadi
                logger.exception("UserContextMiddleware: ban xabarini yuborishda XATO")
            return None

        return await handler(event, data)
