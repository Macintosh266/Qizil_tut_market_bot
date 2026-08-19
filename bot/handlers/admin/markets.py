from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.market_repo import (
    create_market,
    delete_market,
    get_market_by_name,
)
from bot.filters import IsAdmin
from bot.lexicons import get_employe_text
from bot.utils.args import parse_quoted_args

router = Router(name="admin_markets")
router.message.filter(IsAdmin())


@router.message(Command("add_market"))
async def add_market(message: Message, command: CommandObject, session: AsyncSession, lang: str):
    usage = '/add_market "Do\'kon nomi" "Do\'kon manzili"'
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    args = parse_quoted_args(command.args)
    if len(args) < 2:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    name, address = args[0], args[1]
    market = await create_market(session, name=name, address=address)
    await message.answer(get_employe_text("market_added", lang, name=market.name))


@router.message(Command("delete_market"))
async def delete_market_cmd(message: Message, command: CommandObject, session: AsyncSession, lang: str):
    usage = '/delete_market "Do\'kon nomi" "Do\'kon manzili"'
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    args = parse_quoted_args(command.args)
    name = args[0] if args else ""
    market = await get_market_by_name(session, name)
    if not market:
        await message.answer(get_employe_text("market_not_found", lang))
        return

    await delete_market(session, market)
    await message.answer(get_employe_text("market_deleted", lang, name=market.name))
