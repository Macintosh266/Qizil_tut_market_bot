from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.user_repo import (
    set_user_address,
    update_user_language,
    update_user_name,
)
from bot.enums.enum import Language, UserRole
from bot.keyboards.admin_kb import admin_panel_kb, market_admin_panel_kb
from bot.keyboards.user_kb import (
    address_input_kb,
    language_kb,
    main_menu_kb,
    settings_kb,
)
from bot.lexicons import get_text
from bot.models import UserModel
from bot.states import SettingsStates

router = Router(name="settings")


def _return_kb(lang: str, db_user: UserModel):
    """
    Sozlamalar tugagach qaysi klaviaturaga qaytish kerakligini aniqlaydi:
    SUPER_ADMIN -> to'liq admin panel, ADMIN -> o'z do'koni paneli,
    aks holda oddiy asosiy menyu.
    """
    if db_user.role == UserRole.SUPER_ADMIN:
        return admin_panel_kb(lang)
    if db_user.role == UserRole.ADMIN:
        return market_admin_panel_kb(lang)
    return main_menu_kb(lang, is_admin=False)


@router.message(F.text.func(lambda t: t in [get_text("menu_settings", l) for l in ("uz", "ru", "en")]))
async def show_settings(message: Message, lang: str):
    await message.answer(get_text("settings_menu", lang), reply_markup=settings_kb(lang))


@router.callback_query(F.data == "settings:lang")
async def ask_new_language(callback: CallbackQuery, lang: str):
    await callback.message.edit_text(get_text("choose_language", lang), reply_markup=language_kb())
    await callback.answer()


async def _is_registered(event: CallbackQuery, db_user: UserModel | None = None) -> bool:
    # Agar foydalanuvchi hali ro'yxatdan o'tmagan bo'lsa (Registration oqimida),
    # bu handler ishlamaydi va callback keyingi (start.py dagi) handlerga o'tadi.
    return db_user is not None


@router.callback_query(F.data.startswith("lang:"), _is_registered)
async def set_new_language(callback: CallbackQuery, session: AsyncSession, db_user: UserModel):
    new_lang = callback.data.split(":")[1]
    await update_user_language(session, db_user, Language(new_lang))
    await callback.message.edit_text(get_text("saved", new_lang))
    await callback.message.answer("📋", reply_markup=_return_kb(new_lang, db_user))
    await callback.answer()


@router.callback_query(F.data == "settings:address")
async def ask_new_address(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(SettingsStates.waiting_new_address)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(get_text("enter_address", lang), reply_markup=address_input_kb(lang))
    await callback.answer()


@router.message(SettingsStates.waiting_new_address, F.text.func(lambda t: t in [get_text("back_btn", l) for l in ("uz", "ru", "en")]))
async def cancel_new_address(message: Message, lang: str, state: FSMContext, db_user: UserModel):
    await state.clear()
    await message.answer(get_text("canceled", lang), reply_markup=_return_kb(lang, db_user))


@router.message(SettingsStates.waiting_new_address, F.location)
async def save_new_address_from_location(
    message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel
):
    await set_user_address(
        session,
        db_user.id,
        get_text("location_saved_address", lang),
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )
    await state.clear()
    await message.answer(get_text("saved", lang), reply_markup=_return_kb(lang, db_user))


@router.message(SettingsStates.waiting_new_address, F.text)
async def save_new_address(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    await set_user_address(session, db_user.id, message.text.strip())
    await state.clear()
    await message.answer(get_text("saved", lang), reply_markup=_return_kb(lang, db_user))


@router.callback_query(F.data == "settings:name")
async def ask_new_name(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(SettingsStates.waiting_new_name)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(get_text("enter_new_name", lang))
    await callback.answer()


@router.message(SettingsStates.waiting_new_name, F.text)
async def save_new_name(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    await update_user_name(session, db_user, message.text.strip())
    await state.clear()
    await message.answer(get_text("saved", lang), reply_markup=_return_kb(lang, db_user))
