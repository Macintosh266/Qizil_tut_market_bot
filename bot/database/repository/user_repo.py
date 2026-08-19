from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.enums.enum import Language, UserRole
from bot.models import Address, UserModel


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> UserModel | None:
    result = await session.execute(
        select(UserModel).where(UserModel.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_id_or_username(
    session: AsyncSession, identifier: str
) -> UserModel | None:
    """identifier - user_id (raqam) yoki @username / username bo'lishi mumkin."""
    identifier = identifier.lstrip("@")
    conditions = [UserModel.username == identifier]
    if identifier.isdigit():
        conditions.append(UserModel.telegram_id == int(identifier))
    result = await session.execute(select(UserModel).where(or_(*conditions)))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    full_name: str,
    username: str | None,
    language: Language,
    role: UserRole = UserRole.USER,
) -> UserModel:
    user = UserModel(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username,
        language=language,
        role=role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_phone(session: AsyncSession, user: UserModel, phone: str) -> None:
    user.phone_number = phone
    await session.commit()


async def update_user_language(session: AsyncSession, user: UserModel, language: Language) -> None:
    user.language = language
    await session.commit()


async def update_user_name(session: AsyncSession, user: UserModel, name: str) -> None:
    user.full_name = name
    await session.commit()


async def set_user_role(
    session: AsyncSession, user: UserModel, role: UserRole, market_id: int | None = None
) -> None:
    user.role = role
    user.market_id = market_id  # ADMIN/STAFF uchun do'kon ID, boshqa hollarda None
    await session.commit()


async def set_user_banned(session: AsyncSession, user: UserModel, banned: bool) -> None:
    user.is_banned = banned
    await session.commit()


async def get_active_address(session: AsyncSession, user_id: int) -> Address | None:
    result = await session.execute(
        select(Address).where(Address.user_id == user_id, Address.is_active.is_(True))
    )
    return result.scalar_one_or_none()


async def set_user_address(
    session: AsyncSession,
    user_id: int,
    address_text: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> Address:
    result = await session.execute(
        select(Address).where(Address.user_id == user_id, Address.is_active.is_(True))
    )
    for addr in result.scalars().all():
        addr.is_active = False

    new_address = Address(
        user_id=user_id,
        address=address_text,
        latitude=latitude,
        longitude=longitude,
        is_active=True,
    )
    session.add(new_address)
    await session.commit()
    await session.refresh(new_address)
    return new_address


async def count_staff(session: AsyncSession, market_id: int | None = None) -> int:
    query = select(UserModel).where(UserModel.role == UserRole.STAFF)
    if market_id is not None:
        query = query.where(UserModel.market_id == market_id)
    result = await session.execute(query)
    return len(result.scalars().all())


async def list_admins(session: AsyncSession) -> list[UserModel]:
    """Barcha do'kon adminlari (SUPER_ADMIN kirmaydi) — super-admin uchun global ro'yxat."""
    result = await session.execute(select(UserModel).where(UserModel.role == UserRole.ADMIN))
    return list(result.scalars().all())


async def list_staff(session: AsyncSession, market_id: int | None = None) -> list[UserModel]:
    """market_id berilsa — faqat shu do'konning ishchilari, aks holda barchasi."""
    query = select(UserModel).where(UserModel.role == UserRole.STAFF)
    if market_id is not None:
        query = query.where(UserModel.market_id == market_id)
    result = await session.execute(query)
    return list(result.scalars().all())


async def list_banned_users(session: AsyncSession) -> list[UserModel]:
    result = await session.execute(select(UserModel).where(UserModel.is_banned.is_(True)))
    return list(result.scalars().all())
