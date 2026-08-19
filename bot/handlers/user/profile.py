from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.user_repo import get_active_address
from bot.lexicons import get_text
from bot.models import UserModel

router = Router(name="profile")


@router.message(F.text.func(lambda t: t in [get_text("menu_profile", l) for l in ("uz", "ru", "en")]))
async def show_profile(message: Message, session: AsyncSession, lang: str, db_user: UserModel):
    address = await get_active_address(session, db_user.id)
    await message.answer(
        get_text(
            "profile_info",
            lang,
            id=db_user.telegram_id,
            name=db_user.full_name,
            username=f"@{db_user.username}" if db_user.username else "-",
            language=db_user.language.value.upper(),
            phone=db_user.phone_number or "-",
            address=address.address if address else "-",
        )
    )
