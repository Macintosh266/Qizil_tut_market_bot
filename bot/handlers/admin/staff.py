from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.market_repo import get_all_markets, get_market
from bot.database.repository.user_repo import (
    get_user_by_id_or_username,
    list_staff,
    set_user_role,
)
from bot.enums.enum import UserRole
from bot.filters import IsAdmin
from bot.handlers.admin.base import btn_texts, finish, finish_cb, track_list_message
from bot.keyboards.admin_kb import cancel_kb, markets_select_kb, users_select_kb
from bot.lexicons import get_employe_text
from bot.models import UserModel
from bot.states import AdminPanelStates
from bot.utils.commands import set_commands_for_user

router = Router(name="admin_staff")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ==================== ISHCHI (STAFF) BOSHQARUVI — admin panel (tugmalar) ====================

@router.message(F.text.func(lambda t: t in btn_texts("add_staff_btn")))
async def start_add_staff(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    if db_user.role == UserRole.SUPER_ADMIN:
        # Super-admin har doim qaysi do'kon uchun ishchi qo'shayotganini tanlashi kerak
        markets = await get_all_markets(session)
        if not markets:
            await message.answer(get_employe_text("empty_list", lang))
            return
        await state.update_data(search_context="as_market")
        await state.set_state(AdminPanelStates.searching_market)
        sent = await message.answer(
            get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
            reply_markup=markets_select_kb(markets, "as_market_pick", lang),
        )
        await track_list_message(state, sent)
        return

    # Oddiy (do'konga bog'langan) admin uchun do'kon tanlash shart emas — o'z do'koni ishlatiladi
    await state.update_data(market_id=db_user.market_id)
    await state.set_state(AdminPanelStates.waiting_add_staff_id)
    await message.answer(get_employe_text("add_staff_prompt", lang), reply_markup=cancel_kb(lang))


@router.callback_query(F.data.startswith("as_market_pick:"))
async def pick_add_staff_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market_id)
    await state.set_state(AdminPanelStates.waiting_add_staff_id)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        f"<b>{market.address}</b>\n\n" + get_employe_text("add_staff_prompt", lang),
        reply_markup=cancel_kb(lang),
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_add_staff_id, F.text)
async def process_add_staff_interactive(message: Message, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    data = await state.get_data()
    market_id = data.get("market_id")
    if not market_id:
        await finish(message, state, lang, get_employe_text("market_not_found", lang))
        return

    user = await get_user_by_id_or_username(session, message.text.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return
    await set_user_role(session, user, UserRole.STAFF, market_id=market_id)
    await set_commands_for_user(bot, user.telegram_id, UserRole.STAFF, user.language.value)
    await finish(message, state, lang, get_employe_text("staff_added", lang, name=user.full_name))


@router.message(F.text.func(lambda t: t in btn_texts("delete_staff_btn")))
async def start_delete_staff(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    staff = await list_staff(session, market_id=market_id)
    if not staff:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="ds_user")
    await state.set_state(AdminPanelStates.searching_user)
    sent = await message.answer(
        get_employe_text("choose_staff_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(staff, "ds_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("ds_pick:"))
async def process_delete_staff_interactive(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    user_id = int(callback.data.split(":")[1])
    user = await session.get(UserModel, user_id)
    if not user:
        await callback.answer(get_employe_text("user_not_found", lang), show_alert=True)
        return
    await set_user_role(session, user, UserRole.USER, market_id=None)
    await set_commands_for_user(bot, user.telegram_id, UserRole.USER, user.language.value)
    await finish_cb(callback, state, lang, get_employe_text("staff_removed", lang, name=user.full_name))


@router.message(F.text.func(lambda t: t in btn_texts("staff_list_btn")))
async def show_staff_list(message: Message, session: AsyncSession, lang: str, db_user: UserModel):
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    staff = await list_staff(session, market_id=market_id)
    if not staff:
        await message.answer(get_employe_text("empty_list", lang))
        return
    lines = [f"{s.full_name} (@{s.username})" if s.username else s.full_name for s in staff]
    await message.answer("\n".join(lines))