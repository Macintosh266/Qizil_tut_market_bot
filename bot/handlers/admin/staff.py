from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.user_repo import get_user_by_id_or_username, set_user_role
from bot.enums.enum import UserRole
from bot.filters import IsAdmin
from bot.lexicons import get_employe_text
from bot.utils.commands import set_commands_for_user

router = Router(name="admin_staff")
router.message.filter(IsAdmin())


@router.message(Command("add_staff"))
async def add_staff(message: Message, command: CommandObject, session: AsyncSession, lang: str, bot: Bot):
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage="/add_staff <user_id yoki username>"))
        return

    user = await get_user_by_id_or_username(session, command.args.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return

    await set_user_role(session, user, UserRole.STAFF)
    await set_commands_for_user(bot, user.telegram_id, UserRole.STAFF, user.language.value)
    await message.answer(get_employe_text("staff_added", lang, name=user.full_name))


@router.message(Command("delete_staff"))
async def delete_staff(message: Message, command: CommandObject, session: AsyncSession, lang: str, bot: Bot):
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage="/delete_staff <user_id yoki username>"))
        return

    user = await get_user_by_id_or_username(session, command.args.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return

    await set_user_role(session, user, UserRole.USER)
    await set_commands_for_user(bot, user.telegram_id, UserRole.USER, user.language.value)
    await message.answer(get_employe_text("staff_removed", lang, name=user.full_name))
