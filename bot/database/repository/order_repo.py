from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.repository.product_repo import decrease_stock, get_product
from bot.enums.enum import DeliveryType, OrderStatus
from bot.models import OrderItemModel, OrderModel, StatisticModel


async def create_order_with_statistics(
    session: AsyncSession,
    user_id: int,
    phone: str,
    delivery_type: DeliveryType,
    address: str | None,
    cart_items: dict[int, int],  # {product_id: quantity}
    latitude: float | None = None,
    longitude: float | None = None,
) -> OrderModel:
    """
    Buyurtma, uning OrderItem'lari va har bir mahsulot uchun Statistic
    yozuvini bitta tranzaksiyada yaratadi, hamda ombordagi sonini kamaytiradi.
    """
    total = 0.0
    order = OrderModel(
        user_id=user_id,
        phone=phone,
        delivery_type=delivery_type,
        address=address,
        latitude=latitude,
        longitude=longitude,
        status=OrderStatus.NEW,
    )
    session.add(order)
    await session.flush()  # order.id olish uchun

    for product_id, quantity in cart_items.items():
        product = await get_product(session, product_id)
        if not product:
            continue

        item_price = float(product.price)
        total += item_price * quantity

        order_item = OrderItemModel(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            price=item_price,
        )
        session.add(order_item)
        await session.flush()  # order_item.id olish uchun

        session.add(
            StatisticModel(
                order_id=order.id,
                order_item_id=order_item.id,
                market_id=product.market_id,
                product_id=product_id,
                quantity=quantity,
                price=item_price,
                total_price=item_price * quantity,
                delivery_type=delivery_type,
            )
        )

        await decrease_stock(session, product, quantity)

    order.total_price = total
    await session.commit()
    await session.refresh(order)
    return order


async def get_order(session: AsyncSession, order_id: int) -> OrderModel | None:
    result = await session.execute(
        select(OrderModel)
        .options(selectinload(OrderModel.items).selectinload(OrderItemModel.product))
        .where(OrderModel.id == order_id)
    )
    return result.scalar_one_or_none()


async def get_user_orders(session: AsyncSession, user_id: int) -> list[OrderModel]:
    result = await session.execute(
        select(OrderModel)
        .options(selectinload(OrderModel.items).selectinload(OrderItemModel.product))
        .where(OrderModel.user_id == user_id)
        .order_by(OrderModel.create_data.desc())
    )
    return list(result.scalars().all())


async def get_new_orders(session: AsyncSession) -> list[OrderModel]:
    result = await session.execute(
        select(OrderModel)
        .options(
            selectinload(OrderModel.items).selectinload(OrderItemModel.product),
            selectinload(OrderModel.user),
        )
        .where(OrderModel.status == OrderStatus.NEW)
        .order_by(OrderModel.create_data)
    )
    return list(result.scalars().all())


async def accept_order(session: AsyncSession, order_id: int, staff_user_id: int) -> bool:
    """True — muvaffaqiyatli qabul qilindi, False — buyurtma topilmadi yoki allaqachon qabul qilingan."""
    order = await session.get(OrderModel, order_id)
    if not order:
        return False
    if order.status != OrderStatus.NEW:
        return False

    order.status = OrderStatus.CONFIRMED

    # shu buyurtmaga tegishli statistik yozuvlarga ishchini biriktiramiz
    result = await session.execute(
        select(StatisticModel).where(StatisticModel.order_id == order_id)
    )
    for stat in result.scalars().all():
        stat.staff_id = staff_user_id

    await session.commit()
    return True


async def reject_order(session: AsyncSession, order_id: int) -> bool:
    """True — muvaffaqiyatli rad etildi, False — buyurtma topilmadi yoki allaqachon boshqa holatda."""
    order = await session.get(OrderModel, order_id)
    if not order:
        return False
    if order.status != OrderStatus.NEW:
        return False

    order.status = OrderStatus.CANCELED
    await session.commit()
    return True
