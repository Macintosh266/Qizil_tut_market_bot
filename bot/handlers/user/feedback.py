from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.feedback_repo import create_feedback
from bot.keyboards.user_kb import main_menu_kb
from bot.lexicons import get_text
from bot.models import UserModel
from bot.states import Feedback

router = Router(name="feedback")

_MENU_FEEDBACK_TEXTS = frozenset(get_text("menu_feedback", l) for l in ("uz", "ru", "en"))


@router.message(F.text.func(lambda t: t in _MENU_FEEDBACK_TEXTS))
async def start_feedback(message: Message, state: FSMContext, lang: str):
    await state.set_state(Feedback.waiting_text)
    await message.answer(get_text("feedback_prompt", lang))


@router.message(Feedback.waiting_text, F.text)
async def process_feedback_text(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    await create_feedback(session, user_id=db_user.id, text=message.text.strip())
    await state.clear()
    is_admin = db_user.role.value in ("admin", "super_admin")
    await message.answer(get_text("feedback_sent", lang), reply_markup=main_menu_kb(lang, is_admin=is_admin))
