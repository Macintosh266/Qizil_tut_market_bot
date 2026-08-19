import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from bot.config import settings
from bot.database.engine import init_db
from bot.handlers import get_main_router
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.user_context import UserContextMiddleware
from bot.utils.commands import set_default_commands, set_role_based_commands

logging.basicConfig(level=logging.INFO)

# Windows'da standart ProactorEventLoop asyncpg/psycopg bilan ba'zan mos
# kelmay, ulanish xatolarini beradi. Shu sabab SelectorEventLoop'ga o'tkazamiz.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main() -> None:
    storage = RedisStorage.from_url(settings.redis_url)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # Tartib muhim: avval DB session, keyin shu session orqali db_user/lang aniqlanadi
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(UserContextMiddleware())

    dp.include_router(get_main_router())

    await init_db()

    # Menu (/ tugmasi) komandalarini o'rnatish:
    # - oddiy foydalanuvchilar uchun umumiy ro'yxat (barcha tillarda)
    # - bazadagi mavjud admin/ishchilar uchun shaxsiy (kengaytirilgan) ro'yxat
    await set_default_commands(bot)
    await set_role_based_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot to'xtatildi")
