from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.repository.product_repo import decrease_stock, increase_stock
from bot.enums.enum import DeliveryType, OrderStatus
from bot.models import OrderItemModel, OrderModel, ProductsModel, StatisticModel


class InsufficientStockError(Exception):
    """Buyurtma yaratish paytida mahsulot omborda yetarli emasligi
    aniqlansa ko'tariladi (checkout.py bu xatoni ushlab, mijozga
    tushunarli xabar beradi)."""

    def __init__(self, product_name: str, available: int):
        self.product_name = product_name
        self.available = available
        super().__init__(f"Omborda yetarli emas: {product_name} (mavjud: {available})")


async def get_product_for_update(session: AsyncSession, product_id: int) -> ProductsModel | None:
    """
    Mahsulotni QATOR DARAJASIDA QULFLAB (`SELECT ... FOR UPDATE`) o'qiydi.

    Nega kerak: bu qulflashsiz, agar ikki xaridor BIR VAQTDA (masalan
    omborda 1 dona qolgan mahsulotni) buyurtma qilsa, ikkalasi ham
    "stock=1" ni o'qib, ikkalasi ham muvaffaqiyatli buyurtma bera olardi —
    natijada omborda -1 (yoki noto'g'ri 0) qolib, aslida 2 marta sotilgan
    bo'lib chiqardi ("lost update" muammosi).

    `FOR UPDATE` shu qatorni joriy tranzaksiya commit/rollback bo'lguncha
    qulflab qo'yadi — ikkinchi so'rov birinchisi tugaguncha KUTADI, shundan
    keyingina eng so'nggi (to'g'ri) `stock` qiymatini o'qiydi.
    """
    result = await session.execute(
        select(ProductsModel).where(ProductsModel.id == product_id).with_for_update()
    )
    return result.scalar_one_or_none()


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
        product = await get_product_for_update(session, product_id)
        if not product:
            continue

        if quantity > product.stock:
            # Boshqa xaridor shu orada sotib ulgurgan bo'lishi mumkin —
            # tranzaksiyani bekor qilib, checkout.py'ga aniq xato beramiz.
            await session.rollback()
            raise InsufficientStockError(product.name, product.stock)

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
        .options(
            selectinload(OrderModel.items).selectinload(OrderItemModel.product),
            selectinload(OrderModel.user),
        )
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


async def get_orders_by_status(session: AsyncSession, status: OrderStatus) -> list[OrderModel]:
    """Berilgan holatdagi barcha buyurtmalar (eng yangisidan boshlab).
    Mahsulot+do'kon ma'lumoti bilan birga (eager load) — do'kon bo'yicha
    filtrlashni chaqiruvchi tomonda (Python'da) qilish uchun."""
    result = await session.execute(
        select(OrderModel)
        .options(
            selectinload(OrderModel.items).selectinload(OrderItemModel.product),
            selectinload(OrderModel.user),
        )
        .where(OrderModel.status == status)
        .order_by(OrderModel.create_data.desc())
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
    """True — muvaffaqiyatli rad etildi, False — buyurtma topilmadi yoki allaqachon boshqa holatda.

    Buyurtma yaratilganda ombordagi son darhol kamaytirilib, statistika
    yozuvi yaratilgan edi (mijoz tasdiqlagan zahoti, admin javobidan oldin).
    Endi rad etilganda buni ORTGA QAYTARAMIZ: har bir mahsulotning
    ombordagi sonini tiklaymiz va shu buyurtmaga tegishli statistika
    yozuvlarini o'chiramiz — aks holda sotilmagan mahsulot statistikada
    "sotilgan" bo'lib qolar edi.
    """
    result = await session.execute(
        select(OrderModel)
        .options(selectinload(OrderModel.items).selectinload(OrderItemModel.product))
        .where(OrderModel.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        return False
    if order.status != OrderStatus.NEW:
        return False

    for item in order.items:
        if item.product:
            await increase_stock(session, item.product, item.quantity)

    await session.execute(delete(StatisticModel).where(StatisticModel.order_id == order_id))

    order.status = OrderStatus.CANCELED
    await session.commit()
    return True