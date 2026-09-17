from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.order_repo import get_order, get_orders_by_status
from bot.enums.enum import DeliveryType, OrderStatus, UserRole
from bot.filters import IsAdmin
from bot.handlers.admin.base import btn_texts
from bot.keyboards.admin_kb import order_detail_action_kb, order_detail_back_kb, orders_page_kb, orders_status_kb
from bot.lexicons import get_employe_text
from bot.models import UserModel

router = Router(name="admin_orders_list")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

PAGE_SIZE = 10

_STATUS_MAP = {
    "new": OrderStatus.NEW,
    "confirmed": OrderStatus.CONFIRMED,
    "canceled": OrderStatus.CANCELED,
}


def _belongs_to_admin(db_user: UserModel, order) -> bool:
    """SUPER_ADMIN barcha buyurtmalarni ko'radi. Oddiy ADMIN esa faqat
    BARCHA mahsulotlari o'z do'koniga tegishli bo'lgan buyurtmalarni."""
    if db_user.role == UserRole.SUPER_ADMIN:
        return True
    market_ids = {item.product.market_id for item in order.items if item.product}
    return market_ids == {db_user.market_id}


def _paginate(items: list, page: int) -> tuple[list, int, int]:
    total_pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    return items[start : start + PAGE_SIZE], page, total_pages


async def _render_orders(
    target: Message, session: AsyncSession, lang: str, db_user: UserModel, status_key: str, page: int, edit: bool
) -> None:
    status = _STATUS_MAP.get(status_key)
    if status is None:
        return

    all_orders = await get_orders_by_status(session, status)
    orders = [o for o in all_orders if _belongs_to_admin(db_user, o)]

    if not orders:
        text = get_employe_text("no_orders_in_status", lang)
        if edit:
            try:
                await target.edit_text(text)
                return
            except Exception:
                pass
        await target.answer(text)
        return

    page_orders, page, total_pages = _paginate(orders, page)
    status_label = get_employe_text(f"order_status_{status_key}", lang)
    text = get_employe_text("orders_list_title", lang, status=status_label)
    keyboard = orders_page_kb(page_orders, status_key, page, total_pages, lang)

    if edit:
        try:
            await target.edit_text(text, reply_markup=keyboard)
            return
        except Exception:
            pass
    await target.answer(text, reply_markup=keyboard)


@router.message(F.text.func(lambda t: t in btn_texts("orders_list_btn")))
async def open_orders_list(message: Message, lang: str):
    await message.answer(get_employe_text("choose_order_status", lang), reply_markup=orders_status_kb(lang))


@router.callback_query(F.data.startswith("ord_status:"))
async def show_status_orders(callback: CallbackQuery, session: AsyncSession, lang: str, db_user: UserModel):
    status_key = callback.data.split(":")[1]
    await _render_orders(callback.message, session, lang, db_user, status_key, 0, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("ord_page:"))
async def paginate_orders(callback: CallbackQuery, session: AsyncSession, lang: str, db_user: UserModel):
    _, status_key, page = callback.data.split(":")
    await _render_orders(callback.message, session, lang, db_user, status_key, int(page), edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("ord_view:"))
async def view_order_detail(callback: CallbackQuery, session: AsyncSession, lang: str, db_user: UserModel):
    _, order_id, status_key, page = callback.data.split(":")
    order = await get_order(session, int(order_id))
    if not order or not _belongs_to_admin(db_user, order):
        await callback.answer(get_employe_text("order_not_found", lang), show_alert=True)
        return

    items_text = "\n".join(f"• {i.product.name} x{i.quantity}" for i in order.items if i.product) or "-"

    if order.delivery_type == DeliveryType.PICKUP:
        delivery_info = get_employe_text("delivery_info_pickup", lang)
    elif order.latitude is not None and order.longitude is not None:
        delivery_info = get_employe_text("delivery_info_delivery_location", lang)
    else:
        delivery_info = get_employe_text("delivery_info_delivery", lang, address=order.address or "-")

    status_label = get_employe_text(f"order_status_{status_key}", lang)
    text = get_employe_text(
        "order_detail",
        lang,
        order_id=order.id,
        status=status_label,
        customer=order.user.full_name if order.user else "-",
        phone=order.phone,
        delivery_info=delivery_info,
        items=items_text,
        total=f"{order.total_price:,.0f}",
    )

    if order.status == OrderStatus.NEW:
        keyboard = order_detail_action_kb(order.id, status_key, int(page), lang)
    else:
        keyboard = order_detail_back_kb(status_key, int(page), lang)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)

    if order.latitude is not None and order.longitude is not None:
        # Manzil (lokatsiya) alohida xabar turi — matnli xabarni lokatsiyaga
        # aylantirib bo'lmaydi, shuning uchun bu faqat shu holatda qo'shimcha
        # xabar sifatida yuboriladi.
        try:
            await callback.message.answer_location(latitude=float(order.latitude), longitude=float(order.longitude))
        except Exception:
            pass

    await callback.answer()
