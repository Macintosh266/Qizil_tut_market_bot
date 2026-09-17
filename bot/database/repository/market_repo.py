from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import MarketModel
from bot.utils.crypto import decrypt_value, encrypt_value


async def get_all_markets(session: AsyncSession) -> list[MarketModel]:
    result = await session.execute(
        select(MarketModel).where(MarketModel.is_active.is_(True))
    )
    return list(result.scalars().all())


async def get_market_by_name(session: AsyncSession, name: str) -> MarketModel | None:
    result = await session.execute(select(MarketModel).where(MarketModel.name == name))
    return result.scalar_one_or_none()


async def get_market(session: AsyncSession, market_id: int) -> MarketModel | None:
    return await session.get(MarketModel, market_id)


async def create_market(session: AsyncSession, name: str, address: str) -> MarketModel:
    market = MarketModel(name=name, address=address)
    session.add(market)
    await session.commit()
    await session.refresh(market)
    return market


async def delete_market(session: AsyncSession, market: MarketModel) -> None:
    market.is_active = False
    await session.commit()


async def reactivate_market(session: AsyncSession, market: MarketModel, address: str) -> MarketModel:
    """Avval o'chirilgan (is_active=False) do'konni xuddi shu nom bilan qayta
    faollashtiradi. `name` ustuni unique bo'lgani uchun create_market() bilan
    qayta yaratib bo'lmaydi — shu funksiya o'sha muammoni oldini oladi."""
    market.is_active = True
    market.address = address
    await session.commit()
    await session.refresh(market)
    return market


async def count_markets(session: AsyncSession) -> int:
    result = await session.execute(
        select(MarketModel).where(MarketModel.is_active.is_(True))
    )
    return len(result.scalars().all())


# ==================== Billz.io integratsiyasi ====================
# Har bir do'kon Billz'da o'zining alohida akkauntiga (alohida API
# kalitiga) ega — shuning uchun "bog'langan" degani `billz_secret_key`
# o'rnatilgan degani (`billz_shop_id` endi ishlatilmaydi, lekin bazada
# orqaga moslik uchun qoldirilgan).

async def get_markets_linked_to_billz(session: AsyncSession) -> list[MarketModel]:
    result = await session.execute(select(MarketModel).where(MarketModel.billz_secret_key.is_not(None)))
    return list(result.scalars().all())


async def get_unlinked_markets(session: AsyncSession) -> list[MarketModel]:
    """Billz kalitiga hali bog'lanmagan do'konlar — bog'lash ekranida ishlatiladi."""
    result = await session.execute(
        select(MarketModel).where(MarketModel.is_active.is_(True), MarketModel.billz_secret_key.is_(None))
    )
    return list(result.scalars().all())


async def set_market_billz_credentials(session: AsyncSession, market: MarketModel, secret_key: str | None) -> None:
    """`secret_key` bazaga yozishdan oldin SHIFRLANADI (`bot/utils/crypto.py`)
    — bazada hech qachon ochiq matn (plaintext) holda saqlanmaydi."""
    market.billz_secret_key = encrypt_value(secret_key) if secret_key else None
    await session.commit()


def get_market_billz_secret_key(market: MarketModel) -> str | None:
    """Bazadagi SHIFRLANGAN kalitni ochib (deshifrlab) qaytaradi. Billz'ga
    haqiqiy so'rov yuborish kerak bo'lgan har bir joyda shu funksiya
    ishlatilishi kerak — `market.billz_secret_key`ning o'zi shifrlangan
    holda, to'g'ridan-to'g'ri ishlatib bo'lmaydi."""
    if not market.billz_secret_key:
        return None
    return decrypt_value(market.billz_secret_key)


async def is_market_billz_managed(session: AsyncSession, market_id: int) -> bool:
    """Shu do'kon Billz bilan bog'langanmi (ya'ni mahsulotlari qo'lda emas,
    faqat Billz orqali boshqarilishi kerakmi)."""
    market = await get_market(session, market_id)
    return bool(market and market.billz_secret_key)