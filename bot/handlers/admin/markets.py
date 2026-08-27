from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.market_repo import (
    create_market,
    delete_market,
    get_all_markets,
    get_market,
    get_market_by_name,
    reactivate_market,
)
from bot.filters import IsAdmin, IsSuperAdmin
from bot.handlers.admin.base import CONFIRM_TEXTS, btn_texts, finish, track_list_message
from bot.keyboards.admin_kb import cancel_kb, confirm_kb, markets_select_kb
from bot.lexicons import get_employe_text
from bot.states import AdminPanelStates

router = Router(name="admin_markets")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ==================== DO'KON BOSHQARUVI — admin panel (tugmalar) ====================

@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("add_market_btn")))
async def start_add_market(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_add_market_name)
    await message.answer(get_employe_text("add_market_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_market_name, F.text)
async def process_market_name(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    name = message.text.strip()
    existing = await get_market_by_name(session, name)

    if existing and existing.is_active:
        # Faol do'kon shu nom bilan allaqachon bor — rad etamiz
        await message.answer(get_employe_text("market_name_exists", lang))
        return

    # existing bo'lsa (avval o'chirilgan) — keyingi bosqichda qayta
    # faollashtiramiz; bo'lmasa, yangi do'kon yaratiladi.
    await state.update_data(
        market_name=name,
        reactivate_market_id=existing.id if existing else None,
    )
    await state.set_state(AdminPanelStates.waiting_add_market_address)
    await message.answer(get_employe_text("add_market_address_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_market_address, F.text)
async def process_market_address(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    address = message.text.strip()
    reactivate_market_id = data.get("reactivate_market_id")

    if reactivate_market_id:
        existing = await get_market(session, reactivate_market_id)
        market = await reactivate_market(session, existing, address)
    else:
        market = await create_market(session, name=data["market_name"], address=address)

    await finish(message, state, lang, get_employe_text("market_added", lang, name=market.name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("delete_market_btn")))
async def start_delete_market(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="del_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "del_market_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("del_market_pick:"))
async def pick_delete_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market.id)
    await state.set_state(AdminPanelStates.waiting_confirm_delete_market)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_employe_text("confirm_delete_market", lang, name=market.name), reply_markup=confirm_kb(lang)
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_confirm_delete_market, F.text.func(lambda t: t in CONFIRM_TEXTS))
async def process_confirm_delete_market(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    market = await get_market(session, data["market_id"])
    if market:
        await delete_market(session, market)
    await finish(message, state, lang, get_employe_text("market_deleted", lang, name=market.name if market else ""))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("market_list_btn")))
async def show_market_list(message: Message, session: AsyncSession, lang: str):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    lines = [f"{m.name} — {m.address}" for m in markets]
    await message.answer("\n".join(lines))