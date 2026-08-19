from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.market_repo import get_all_markets, get_market
from bot.database.repository.user_repo import (
    get_user_by_id_or_username,
    list_admins,
    set_user_role,
)
from bot.enums.enum import UserRole
from bot.filters import IsAdmin, IsSuperAdmin
from bot.handlers.admin.base import btn_texts, finish, finish_cb, track_list_message
from bot.keyboards.admin_kb import cancel_kb, markets_select_kb, users_select_kb
from bot.lexicons import get_employe_text
from bot.models import UserModel
from bot.states import AdminPanelStates
from bot.utils.commands import set_commands_for_user

router = Router(name="admin_admins")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("add_admin_btn")))
async def start_add_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="aa_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "aa_market_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("aa_market_pick:"))
async def pick_add_admin_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market_id)
    await state.set_state(AdminPanelStates.waiting_add_admin_id)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        f"<b>{market.address}</b>\n\n" + get_employe_text("add_admin_prompt", lang),
        reply_markup=cancel_kb(lang),
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_add_admin_id, F.text)
async def process_add_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    data = await state.get_data()
    market_id = data.get("market_id")
    if not market_id:
        await finish(message, state, lang, get_employe_text("market_not_found", lang))
        return

    user = await get_user_by_id_or_username(session, message.text.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return
    await set_user_role(session, user, UserRole.ADMIN, market_id=market_id)
    await set_commands_for_user(bot, user.telegram_id, UserRole.ADMIN, user.language.value)
    await finish(message, state, lang, get_employe_text("admin_added", lang, name=user.full_name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("delete_admin_btn")))
async def start_delete_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    admins = await list_admins(session)
    if not admins:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="da_user")
    await state.set_state(AdminPanelStates.searching_user)
    sent = await message.answer(
        get_employe_text("choose_admin_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(admins, "da_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("da_pick:"))
async def process_delete_admin(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    user_id = int(callback.data.split(":")[1])
    user = await session.get(UserModel, user_id)
    if not user:
        await callback.answer(get_employe_text("user_not_found", lang), show_alert=True)
        return
    await set_user_role(session, user, UserRole.USER, market_id=None)
    await set_commands_for_user(bot, user.telegram_id, UserRole.USER, user.language.value)
    await finish_cb(callback, state, lang, get_employe_text("admin_removed", lang, name=user.full_name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("admin_list_btn")))
async def show_admin_list(message: Message, session: AsyncSession, lang: str):
    admins = await list_admins(session)
    if not admins:
        await message.answer(get_employe_text("empty_list", lang))
        return

    lines = []
    for a in admins:
        market = await get_market(session, a.market_id) if a.market_id else None
        market_label = market.address if market else "—"
        name_label = f"{a.full_name} (@{a.username})" if a.username else a.full_name
        lines.append(f"{name_label} — {market_label}")
    await message.answer("\n".join(lines))