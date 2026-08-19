from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.market_repo import count_markets
from bot.database.repository.product_repo import get_stock_summary
from bot.database.repository.user_repo import count_staff
from bot.enums.enum import DeliveryType
from bot.models import StatisticModel


async def get_period_statistics(
    session: AsyncSession, start: datetime, end: datetime, market_id: int | None = None
) -> dict:
    base_query = select(StatisticModel).where(
        StatisticModel.sold_at >= start, StatisticModel.sold_at < end
    )
    if market_id is not None:
        base_query = base_query.where(StatisticModel.market_id == market_id)

    result = await session.execute(base_query)
    stats = result.scalars().all()

    sold_qty = sum(s.quantity for s in stats)
    sold_sum = sum(float(s.total_price) for s in stats)
    delivered_qty = sum(
        s.quantity for s in stats if s.delivery_type == DeliveryType.DELIVERY
    )
    pickup_qty = sum(
        s.quantity for s in stats if s.delivery_type == DeliveryType.PICKUP
    )

    if market_id is not None:
        markets_count = 1
        staff_count = await count_staff(session, market_id=market_id)
    else:
        markets_count = await count_markets(session)
        staff_count = await count_staff(session)
    stock_qty, stock_sum = await get_stock_summary(session, market_id=market_id)

    return {
        "sold_qty": sold_qty,
        "sold_sum": sold_sum,
        "delivered_qty": delivered_qty,
        "pickup_qty": pickup_qty,
        "markets_count": markets_count,
        "staff_count": staff_count,
        "stock_qty": stock_qty,
        "stock_sum": stock_sum,
    }


async def get_top_products(
    session: AsyncSession, start: datetime, end: datetime, limit: int = 10
) -> list[tuple[int, int, float]]:
    """[(product_id, jami_sotilgan_dona, jami_summa), ...] eng ko'p sotilganlar bo'yicha."""
    query = (
        select(
            StatisticModel.product_id,
            func.sum(StatisticModel.quantity).label("qty"),
            func.sum(StatisticModel.total_price).label("total"),
        )
        .where(StatisticModel.sold_at >= start, StatisticModel.sold_at < end)
        .group_by(StatisticModel.product_id)
        .order_by(func.sum(StatisticModel.quantity).desc())
        .limit(limit)
    )
    result = await session.execute(query)
    return [(row.product_id, row.qty, float(row.total)) for row in result.all()]
