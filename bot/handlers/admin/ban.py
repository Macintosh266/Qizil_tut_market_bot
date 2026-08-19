from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.user_repo import get_user_by_id_or_username, set_user_banned
from bot.filters import IsAdmin
from bot.lexicons import get_employe_text

router = Router(name="admin_ban")
router.message.filter(IsAdmin())


@router.message(Command("ban"))
async def ban_user(message: Message, command: CommandObject, session: AsyncSession, lang: str):
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage="/ban <user_id yoki username>"))
        return

    user = await get_user_by_id_or_username(session, command.args.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return

    await set_user_banned(session, user, True)
    await message.answer(get_employe_text("user_banned", lang, name=user.full_name))


@router.message(Command("unban"))
async def unban_user(message: Message, command: CommandObject, session: AsyncSession, lang: str):
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage="/unban <user_id yoki username>"))
        return

    user = await get_user_by_id_or_username(session, command.args.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return

    await set_user_banned(session, user, False)
    await message.answer(get_employe_text("user_unbanned", lang, name=user.full_name))
