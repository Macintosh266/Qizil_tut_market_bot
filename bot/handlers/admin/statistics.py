from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.statistic_repo import get_period_statistics
from bot.filters import IsAdmin
from bot.lexicons import get_employe_text
from bot.utils.period import parse_period

router = Router(name="admin_statistics")
router.message.filter(IsAdmin())


@router.message(Command("statistic"))
async def statistic_cmd(message: Message, command: CommandObject, session: AsyncSession, lang: str):
    if not command.args:
        await message.answer(
            get_employe_text(
                "usage", lang, usage="/statistic <kun.oy.yil | oy.yil | yil>, masalan: /statistic 11.08.2026"
            )
        )
        return

    parsed = parse_period(command.args.strip())
    if not parsed:
        await message.answer(get_employe_text("invalid_period", lang))
        return

    start, end, label = parsed
    stats = await get_period_statistics(session, start, end)

    await message.answer(
        get_employe_text("statistic_title", lang, period=label)
        + "\n\n"
        + get_employe_text(
            "statistic_body",
            lang,
            markets_count=stats["markets_count"],
            staff_count=stats["staff_count"],
            sold_qty=stats["sold_qty"],
            delivered_qty=stats["delivered_qty"],
            pickup_qty=stats["pickup_qty"],
            sold_sum=f"{stats['sold_sum']:,.0f}",
            stock_qty=stats["stock_qty"],
            stock_sum=f"{stats['stock_sum']:,.0f}",
        )
    )
