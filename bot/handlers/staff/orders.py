from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.order_repo import accept_order, get_order, reject_order
from bot.enums.enum import UserRole
from bot.filters import IsAdmin
from bot.lexicons import get_employe_text, get_text
from bot.models import UserModel

router = Router(name="admin_orders")
router.callback_query.filter(IsAdmin())


def _order_belongs_to_admin(db_user: UserModel, order) -> bool:
    """SUPER_ADMIN istalgan buyurtmaga javob bera oladi. Oddiy ADMIN esa
    faqat BARCHA mahsulotlari o'z do'koniga tegishli bo'lgan buyurtmaga
    javob bera oladi."""
    if db_user.role == UserRole.SUPER_ADMIN:
        return True
    market_ids = {item.product.market_id for item in order.items if item.product}
    return market_ids == {db_user.market_id}


@router.callback_query(F.data.startswith("staff_accept:"))
async def accept_order_cb(callback: CallbackQuery, session: AsyncSession, lang: str, bot: Bot, db_user: UserModel):
    order_id = int(callback.data.split(":")[1])

    order = await get_order(session, order_id)
    if not order or not _order_belongs_to_admin(db_user, order):
        await callback.answer(get_employe_text("order_already_accepted", lang, order_id=order_id), show_alert=True)
        return

    success = await accept_order(session, order_id, db_user.id)

    if not success:
        await callback.answer(get_employe_text("order_already_accepted", lang, order_id=order_id), show_alert=True)
        return

    await callback.message.edit_text(
        callback.message.text + "\n\n" + get_employe_text("order_accepted", lang, order_id=order_id)
    )
    await callback.answer()

    # Mijozga buyurtmasi qabul qilingani haqida xabar yuboramiz
    order = await get_order(session, order_id)
    if order and order.user:
        try:
            await bot.send_message(
                order.user.telegram_id,
                get_text("order_accepted_customer", order.user.language.value, order_id=order_id),
            )
        except Exception:
            pass


@router.callback_query(F.data.startswith("staff_reject:"))
async def reject_order_cb(callback: CallbackQuery, session: AsyncSession, lang: str, bot: Bot, db_user: UserModel):
    order_id = int(callback.data.split(":")[1])

    order = await get_order(session, order_id)
    if not order or not _order_belongs_to_admin(db_user, order):
        await callback.answer(get_employe_text("order_already_accepted", lang, order_id=order_id), show_alert=True)
        return

    success = await reject_order(session, order_id)

    if not success:
        await callback.answer(get_employe_text("order_already_accepted", lang, order_id=order_id), show_alert=True)
        return

    await callback.message.edit_text(
        callback.message.text + "\n\n" + get_employe_text("order_rejected", lang, order_id=order_id)
    )
    await callback.answer()

    # Mijozga buyurtmasi rad etilgani haqida xabar yuboramiz
    order = await get_order(session, order_id)
    if order and order.user:
        try:
            await bot.send_message(
                order.user.telegram_id,
                get_text("order_rejected_customer", order.user.language.value, order_id=order_id),
            )
        except Exception:
            pass