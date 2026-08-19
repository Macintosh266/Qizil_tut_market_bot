from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.category_repo import get_or_create_category
from bot.database.repository.market_repo import get_market_by_name
from bot.database.repository.product_repo import (
    create_product,
    delete_product,
    get_product_by_market_and_name,
)
from bot.filters import IsAdmin
from bot.lexicons import get_employe_text
from bot.utils.args import parse_quoted_args

router = Router(name="admin_products")
router.message.filter(IsAdmin())


@router.message(Command("add_product"))
async def add_product(message: Message, command: CommandObject, session: AsyncSession, lang: str):
    usage = '/add_product "Do\'kon nomi" "Mahsulot nomi" <soni> <narhi> ["Kategoriya"]'
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    args = parse_quoted_args(command.args)
    if len(args) < 4:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    market_name, product_name, qty_str, price_str = args[0], args[1], args[2], args[3]
    category_name = args[4] if len(args) > 4 else "Umumiy"

    market = await get_market_by_name(session, market_name)
    if not market:
        await message.answer(get_employe_text("market_not_found", lang))
        return

    try:
        quantity = int(qty_str)
        price = float(price_str)
    except ValueError:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    category = await get_or_create_category(session, category_name)
    product = await create_product(
        session,
        market_id=market.id,
        category_id=category.id,
        name=product_name,
        price=price,
        stock=quantity,
    )
    await message.answer(get_employe_text("product_added", lang, name=product.name))


@router.message(Command("delete_product"))
async def delete_product_cmd(message: Message, command: CommandObject, session: AsyncSession, lang: str):
    usage = '/delete_product "Do\'kon nomi" "Mahsulot nomi"'
    if not command.args:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    args = parse_quoted_args(command.args)
    if len(args) < 2:
        await message.answer(get_employe_text("usage", lang, usage=usage))
        return

    market_name, product_name = args[0], args[1]
    market = await get_market_by_name(session, market_name)
    if not market:
        await message.answer(get_employe_text("market_not_found", lang))
        return

    product = await get_product_by_market_and_name(session, market.id, product_name)
    if not product:
        await message.answer(get_employe_text("product_not_found", lang))
        return

    await delete_product(session, product)
    await message.answer(get_employe_text("product_deleted", lang, name=product.name))
