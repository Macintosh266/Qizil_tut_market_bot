from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.models import FeedbackModel


async def create_feedback(session: AsyncSession, user_id: int, text: str) -> FeedbackModel:
    feedback = FeedbackModel(user_id=user_id, text=text)
    session.add(feedback)
    await session.commit()
    await session.refresh(feedback)
    return feedback


async def count_feedbacks(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(FeedbackModel))
    return result.scalar_one()


async def get_feedback_at_offset(session: AsyncSession, offset: int) -> FeedbackModel | None:
    """Barcha fikrlar ro'yxatida (eng yangisidan boshlab) `offset`-o'rindagi
    bitta fikrni qaytaradi — admin panelda birma-bir ko'rish (pagination) uchun."""
    result = await session.execute(
        select(FeedbackModel)
        .options(joinedload(FeedbackModel.user))
        .order_by(FeedbackModel.id.desc())
        .offset(max(0, offset))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_feedback(session: AsyncSession, feedback_id: int) -> FeedbackModel | None:
    return await session.get(FeedbackModel, feedback_id)


async def mark_feedback_reviewed(session: AsyncSession, feedback: FeedbackModel) -> None:
    feedback.is_reviewed = True
    await session.commit()
