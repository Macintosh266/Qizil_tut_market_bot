from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.feedback_repo import (
    count_feedbacks,
    get_feedback,
    get_feedback_at_offset,
    mark_feedback_reviewed,
)
from bot.filters import IsAdmin
from bot.handlers.admin.base import btn_texts
from bot.keyboards.admin_kb import feedback_nav_kb
from bot.lexicons import get_employe_text

router = Router(name="admin_feedbacks")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def _format_feedback(feedback, offset: int, total: int, lang: str) -> str:
    username = f" (@{feedback.user.username})" if feedback.user and feedback.user.username else ""
    name = feedback.user.full_name if feedback.user else "-"
    status = get_employe_text(
        "feedback_status_reviewed" if feedback.is_reviewed else "feedback_status_new", lang
    )
    return get_employe_text(
        "feedback_view",
        lang,
        index=offset + 1,
        total=total,
        name=name,
        username=username,
        text=feedback.text,
        status=status,
    )


async def _send_feedback_page(target: Message, session: AsyncSession, lang: str, offset: int, edit: bool = False):
    total = await count_feedbacks(session)
    if total == 0:
        text = get_employe_text("feedback_empty", lang)
        if edit:
            await target.edit_text(text)
        else:
            await target.answer(text)
        return

    offset = max(0, min(offset, total - 1))
    feedback = await get_feedback_at_offset(session, offset)
    text = _format_feedback(feedback, offset, total, lang)
    kb = feedback_nav_kb(offset, total, feedback.is_reviewed, feedback.id, lang)

    if edit:
        await target.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.message(F.text.func(lambda t: t in btn_texts("feedback_management_btn")))
async def open_feedback_list(message: Message, session: AsyncSession, lang: str):
    await _send_feedback_page(message, session, lang, offset=0, edit=False)


@router.callback_query(F.data.startswith("fb_nav:"))
async def navigate_feedback(callback: CallbackQuery, session: AsyncSession, lang: str):
    offset = int(callback.data.split(":")[1])
    await _send_feedback_page(callback.message, session, lang, offset=offset, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("fb_mark:"))
async def mark_feedback_as_reviewed(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, feedback_id, offset = callback.data.split(":")
    feedback = await get_feedback(session, int(feedback_id))
    if feedback:
        await mark_feedback_reviewed(session, feedback)
        await callback.answer(get_employe_text("feedback_marked_reviewed", lang))
    else:
        await callback.answer()

    await _send_feedback_page(callback.message, session, lang, offset=int(offset), edit=True)


@router.callback_query(F.data == "fb_close")
async def close_feedback_view(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()
