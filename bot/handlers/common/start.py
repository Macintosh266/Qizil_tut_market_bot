from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.repository.user_repo import (
    create_user,
    get_user_by_telegram_id,
    update_user_phone,
)
from bot.enums.enum import Language, UserRole
from bot.lexicons import get_text
from bot.lexicons import get_employe_text
from bot.keyboards.user_kb import language_kb, main_menu_kb, phone_request_kb
from bot.models import UserModel
from bot.states import Registration
from bot.utils.commands import set_commands_for_user

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, db_user: UserModel | None, state: FSMContext):
    # /start har doim joriy FSM holatini (agar biror jarayonda "qotib qolgan"
    # bo'lsa ham) to'liq tozalab, botni "qayta ishga tushirish" vazifasini bajaradi
    await state.clear()

    if db_user:
        lang = db_user.language.value
        await message.answer(
            get_text("welcome", lang, name=db_user.full_name),
            reply_markup=main_menu_kb(lang, is_admin=db_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)),
        )
        return

    await state.set_state(Registration.choosing_language)
    await message.answer(get_text("choose_language"), reply_markup=language_kb())


@router.callback_query(Registration.choosing_language, F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await state.update_data(language=lang)
    await state.set_state(Registration.waiting_phone)
    await callback.message.edit_text(get_text("choose_language", lang))
    await callback.message.answer(
        get_text("share_phone", lang), reply_markup=phone_request_kb(lang)
    )
    await callback.answer()


@router.message(Registration.waiting_phone, F.contact)
async def get_phone(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    lang = data.get("language", "uz")

    is_super_admin = message.from_user.id in settings.super_admin_ids
    role = UserRole.SUPER_ADMIN if is_super_admin else UserRole.USER

    user = await create_user(
        session,
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        language=Language(lang),
        role=role,
    )
    await update_user_phone(session, user, message.contact.phone_number)
    await set_commands_for_user(bot, user.telegram_id, role, lang)
    await state.clear()

    await message.answer(
        get_text("welcome", lang, name=user.full_name),
        reply_markup=main_menu_kb(lang, is_admin=role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    )


@router.message(F.text.in_(["/help"]))
async def cmd_help(message: Message, db_user: UserModel | None, lang: str):
    if db_user and db_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        text = get_employe_text("admin_menu", lang) + "\n\n" + get_text("help_user", lang)
    elif db_user and db_user.role == UserRole.STAFF:
        text = get_employe_text("staff_menu", lang) + "\n\n" + get_text("help_user", lang)
    else:
        text = get_text("help_user", lang)
    await message.answer(text)
