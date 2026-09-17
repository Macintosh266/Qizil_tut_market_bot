from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bot.enums.enum import UserRole
from bot.keyboards.user_kb import main_menu_kb
from bot.lexicons import get_text
from bot.models import UserModel

router = Router(name="others")

# DIQQAT: bu router ENG OXIRIDA ulanishi shart (bot/handlers/__init__.py'ga
# qarang). Aks holda bu yerdagi "hammasini ushlab qoluvchi" handlerlar
# boshqa (admin/staff/user) routerlardan OLDIN ishlab ketib, ularni
# butunlay bloklab qo'yadi.


@router.message()
async def unknown_message(message: Message, lang: str, db_user: UserModel | None):
    """Hech qaysi handler yoki FSM holatiga mos kelmagan xabar (matn, rasm,
    fayl va h.k.) uchun yakuniy "tutqich" — foydalanuvchiga bunday buyruq
    yo'qligini bildiradi."""
    is_admin = bool(db_user and db_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN))
    reply_markup = main_menu_kb(lang, is_admin=is_admin) if db_user else None
    await message.answer(get_text("unknown_command", lang), reply_markup=reply_markup)


@router.callback_query()
async def unknown_callback(callback: CallbackQuery, lang: str):
    """Hech qaysi handlerga mos kelmagan inline tugma bosilishi — masalan,
    eskirgan/muddati o'tgan xabardagi tugma bosilganda "yuklanish" holatida
    qotib qolmasligi uchun."""
    await callback.answer(get_text("unknown_command", lang), show_alert=True)