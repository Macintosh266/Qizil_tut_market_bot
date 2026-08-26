from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.order_repo import accept_order, get_order, reject_order
from bot.database.repository.user_repo import get_user_by_telegram_id
from bot.filters import IsAdmin, IsStaff
from bot.lexicons import get_employe_text, get_text

router = Router(name="admin_orders")
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data.startswith("staff_accept:"))
async def accept_order_cb(callback: CallbackQuery, session: AsyncSession, lang: str, bot: Bot):
    order_id = int(callback.data.split(":")[1])
    admin_user = await get_user_by_telegram_id(session, callback.from_user.id)

    success = await accept_order(session, order_id, admin_user.id)

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
async def reject_order_cb(callback: CallbackQuery, session: AsyncSession, lang: str, bot: Bot):
    order_id = int(callback.data.split(":")[1])

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