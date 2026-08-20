from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import MarketModel


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