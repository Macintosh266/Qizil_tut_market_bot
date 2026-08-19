from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from sqlalchemy import select

from bot.database.engine import async_session_maker
from bot.enums.enum import UserRole
from bot.lexicons.lexicon_employe import LEXICON_COMMANDS_ADMIN, LEXICON_COMMANDS_STAFF
from bot.lexicons.lexicon_text import LEXICON_COMMANDS_USER
from bot.models import UserModel


def _to_bot_commands(pairs: list[tuple[str, str]]) -> list[BotCommand]:
    return [BotCommand(command=cmd, description=desc) for cmd, desc in pairs]


async def set_default_commands(bot: Bot) -> None:
    """
    Oddiy foydalanuvchilar uchun menu komandalarini o'rnatadi — har bir til
    uchun alohida (Telegram foydalanuvchining client tili bo'yicha tanlaydi),
    hamda til aniqlanmagan holatlar uchun standart (uz) ro'yxat.
    """
    for lang, pairs in LEXICON_COMMANDS_USER.items():
        await bot.set_my_commands(
            commands=_to_bot_commands(pairs),
            scope=BotCommandScopeDefault(),
            language_code=lang,
        )
    # language_code'siz standart (fallback) ro'yxat
    await bot.set_my_commands(
        commands=_to_bot_commands(LEXICON_COMMANDS_USER["uz"]),
        scope=BotCommandScopeDefault(),
    )


async def set_role_based_commands(bot: Bot) -> None:
    """
    Bazadagi barcha ADMIN va STAFF foydalanuvchilarga shaxsiy (faqat o'sha
    chat uchun) menu komandalarini o'rnatadi — BotCommandScopeChat orqali,
    shu sababli oddiy foydalanuvchilar bu komandalarni ko'rmaydi.
    """
    async with async_session_maker() as session:
        result = await session.execute(
            select(UserModel).where(
                UserModel.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.STAFF])
            )
        )
        staff_and_admins = result.scalars().all()

    for user in staff_and_admins:
        lang = user.language.value
        pairs = (
            LEXICON_COMMANDS_ADMIN.get(lang, LEXICON_COMMANDS_ADMIN["uz"])
            if user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)
            else LEXICON_COMMANDS_STAFF.get(lang, LEXICON_COMMANDS_STAFF["uz"])
        )
        try:
            await bot.set_my_commands(
                commands=_to_bot_commands(pairs),
                scope=BotCommandScopeChat(chat_id=user.telegram_id),
            )
        except Exception:
            # Foydalanuvchi botni bloklagan yoki chat topilmagan bo'lishi mumkin — o'tkazib yuboramiz
            pass


async def set_commands_for_user(bot: Bot, telegram_id: int, role: UserRole, lang: str) -> None:
    """
    Bitta foydalanuvchi uchun komandalarni darhol yangilash — masalan
    /add_admin yoki /add_staff bajarilgandan so'ng shu funksiyani chaqirib,
    yangi adminga/ishchiga tegishli menu darhol ko'rinadigan qilish mumkin.
    """
    if role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        pairs = LEXICON_COMMANDS_ADMIN.get(lang, LEXICON_COMMANDS_ADMIN["uz"])
    elif role == UserRole.STAFF:
        pairs = LEXICON_COMMANDS_STAFF.get(lang, LEXICON_COMMANDS_STAFF["uz"])
    else:
        pairs = LEXICON_COMMANDS_USER.get(lang, LEXICON_COMMANDS_USER["uz"])

    try:
        await bot.set_my_commands(
            commands=_to_bot_commands(pairs),
            scope=BotCommandScopeChat(chat_id=telegram_id),
        )
    except Exception:
        pass
