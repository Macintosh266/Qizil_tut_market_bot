from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.user_repo import (
    get_user_by_id_or_username,
    list_banned_users,
    set_user_banned,
)
from bot.filters import IsAdmin
from bot.handlers.admin.base import btn_texts, finish, finish_cb, track_list_message
from bot.keyboards.admin_kb import cancel_kb, users_select_kb
from bot.lexicons import get_employe_text
from bot.models import UserModel
from bot.states import AdminPanelStates
from bot.enums.enum import UserRole

router = Router(name="admin_ban")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ==================== BAN / UNBAN — admin panel (tugmalar) ====================

@router.message(F.text.func(lambda t: t in btn_texts("ban_user_btn")))
async def start_ban(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_ban_id)
    await message.answer(get_employe_text("ban_user_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_ban_id, F.text)
async def process_ban_interactive(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    user = await get_user_by_id_or_username(session, message.text.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return
    if user.is_banned:
        await finish(message, state, lang, get_employe_text("user_already_banned", lang, name=user.full_name))
        return
    if user.role == UserRole.SUPER_ADMIN:
        await message.answer(get_employe_text("super_admin_ban", lang))
        return

    await set_user_banned(session, user, True)
    await finish(message, state, lang, get_employe_text("user_banned", lang, name=user.full_name))


@router.message(F.text.func(lambda t: t in btn_texts("unban_user_btn")))
async def start_unban(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    banned = await list_banned_users(session)
    if not banned:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="un_user")
    await state.set_state(AdminPanelStates.searching_user)
    sent = await message.answer(
        get_employe_text("choose_banned_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(banned, "un_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("un_pick:"))
async def process_unban_interactive(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    user = await session.get(UserModel, user_id)
    if not user:
        await callback.answer(get_employe_text("user_not_found", lang), show_alert=True)
        return
    await set_user_banned(session, user, False)
    await finish_cb(callback, state, lang, get_employe_text("user_unbanned", lang, name=user.full_name))


