from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.statistic_repo import get_period_statistics
from bot.enums.enum import UserRole
from bot.filters import IsAdmin
from bot.handlers.admin.base import ALL_ADMIN_BUTTON_TEXTS, finish
from bot.lexicons import get_employe_text
from bot.models import UserModel
from bot.states import AdminPanelStates
from bot.utils.period import get_preset_period, parse_period

router = Router(name="admin_statistics")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def _format_statistic(period_label: str, lang: str, stats: dict) -> str:
    return (
        get_employe_text("statistic_title", lang, period=period_label)
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


# ==================== STATISTIKA — admin panel (tayyor davrlar, tugmalar) ====================

@router.callback_query(F.data.startswith("statistic:"))
async def show_preset_statistics(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    preset = callback.data.split(":")[1]
    start, end = get_preset_period(preset)
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    stats = await get_period_statistics(session, start, end, market_id=market_id)
    period_label = get_employe_text(f"statistic_period_{preset}", lang)

    await state.set_state(None)
    await callback.message.edit_text(_format_statistic(period_label, lang, stats))
    await callback.answer()


@router.message(
    AdminPanelStates.waiting_statistic_period,
    F.text,
    F.text.func(lambda t: t not in ALL_ADMIN_BUTTON_TEXTS),
)
async def process_custom_statistic_period(
    message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel
):
    parsed = parse_period(message.text.strip())
    if not parsed:
        await message.answer(get_employe_text("invalid_period", lang))
        return

    start, end, label = parsed
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    stats = await get_period_statistics(session, start, end, market_id=market_id)

    await finish(message, state, lang, _format_statistic(label, lang, stats))