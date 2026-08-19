from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.repository.order_repo import create_order_with_statistics
from bot.database.repository.product_repo import get_product
from bot.database.repository.user_repo import get_active_address, get_user_by_telegram_id
from bot.enums.enum import DeliveryType, UserRole
from bot.lexicons import get_text
from bot.lexicons import get_employe_text
from bot.keyboards.admin_kb import order_action_kb
from bot.keyboards.user_kb import confirm_order_kb, delivery_type_kb, location_request_kb, main_menu_kb
from bot.redis import clear_cart, get_cart
from bot.states import Checkout

router = Router(name="checkout")


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext, lang: str):
    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.answer(get_text("cart_empty", lang), show_alert=True)
        return

    await callback.message.answer(
        get_text("choose_delivery_type", lang), reply_markup=delivery_type_kb(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delivery:"))
async def choose_delivery(callback: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str):
    delivery_type = callback.data.split(":")[1]  # "pickup" | "delivery"
    await state.update_data(delivery_type=delivery_type)

    # Tanlov qilingandan so'ng tugmalar endi kerak emas — o'chirib tashlaymiz,
    # aks holda foydalanuvchi qayta bosib, jarayonni chalkashtirib yuborishi mumkin
    await callback.message.edit_reply_markup(reply_markup=None)

    if delivery_type == "delivery":
        # foydalanuvchining saqlangan manzili bo'lsa taklif qilinadi, aks holda so'raladi
        db_user = await get_user_by_telegram_id(session, callback.from_user.id)
        active_address = await get_active_address(session, db_user.id) if db_user else None
        if active_address:
            await state.update_data(
                address=active_address.address,
                latitude=float(active_address.latitude) if active_address.latitude is not None else None,
                longitude=float(active_address.longitude) if active_address.longitude is not None else None,
            )
            await _show_confirmation(callback.message, session, callback.from_user.id, state, lang)
        else:
            await state.set_state(Checkout.waiting_address)
            await callback.message.answer(get_text("enter_address", lang), reply_markup=location_request_kb(lang))
    else:
        await state.update_data(address=None, latitude=None, longitude=None)
        await _show_confirmation(callback.message, session, callback.from_user.id, state, lang)

    await callback.answer()


@router.message(Checkout.waiting_address, F.location)
async def get_address_from_location(message: Message, state: FSMContext, session: AsyncSession, lang: str):
    await state.update_data(
        address=get_text("location_saved_address", lang),
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )
    await _show_confirmation(message, session, message.from_user.id, state, lang)


@router.message(Checkout.waiting_address, F.text)
async def get_address(message: Message, state: FSMContext, session: AsyncSession, lang: str):
    await state.update_data(address=message.text.strip(), latitude=None, longitude=None)
    await _show_confirmation(message, session, message.from_user.id, state, lang)


async def _show_confirmation(message: Message, session: AsyncSession, telegram_id: int, state: FSMContext, lang: str):
    cart = await get_cart(telegram_id)
    lines, total = [], 0.0
    for product_id, quantity in cart.items():
        product = await get_product(session, product_id)
        if not product:
            continue
        subtotal = float(product.price) * quantity
        total += subtotal
        lines.append(f"{product.name} x{quantity} = {subtotal:,.0f}")

    data = await state.get_data()
    address_line = f"\n📍 {data.get('address')}" if data.get("address") else ""
    text = (
        get_text("order_confirm", lang)
        + "\n\n"
        + "\n".join(lines)
        + f"\n\n{get_text('cart_total', lang)}: {total:,.0f}"
        + address_line
    )
    await state.set_state(Checkout.confirm)
    await message.answer(text, reply_markup=confirm_order_kb(lang))


@router.callback_query(Checkout.confirm, F.data == "order_confirm")
async def confirm_order(callback: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str):
    data = await state.get_data()
    cart = await get_cart(callback.from_user.id)

    if not cart:
        await callback.answer(get_text("cart_empty", lang), show_alert=True)
        await state.clear()
        return

    db_user = await get_user_by_telegram_id(session, callback.from_user.id)
    delivery_type = DeliveryType(data["delivery_type"])

    order = await create_order_with_statistics(
        session,
        user_id=db_user.id,
        phone=db_user.phone_number or "",
        delivery_type=delivery_type,
        address=data.get("address"),
        cart_items=cart,
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    )

    await clear_cart(callback.from_user.id)
    await state.clear()

    await callback.message.edit_text(get_text("order_placed", lang, order_id=order.id))
    await callback.message.answer(
        "📋", reply_markup=main_menu_kb(lang, is_admin=db_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN))
    )

    # Ishchi/adminlarga xabar (super-admin ID'lariga + bazadagi barcha STAFF/ADMIN'larga yuborilishi mumkin;
    # soddalik uchun bu yerda super-adminlarga yuboriladi)
    bot = callback.bot
    for admin_id in settings.super_admin_ids:
        try:
            await bot.send_message(
                admin_id,
                get_employe_text(
                    "new_order_notify",
                    "uz",
                    order_id=order.id,
                    name=db_user.full_name,
                    phone=db_user.phone_number or "-",
                    total=f"{order.total_price:,.0f}",
                ),
                reply_markup=order_action_kb(order.id, "uz"),
            )
            if order.latitude is not None and order.longitude is not None:
                await bot.send_location(admin_id, latitude=float(order.latitude), longitude=float(order.longitude))
        except Exception:
            pass

    await callback.answer()


@router.callback_query(Checkout.confirm, F.data == "order_cancel")
async def cancel_order(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    await callback.message.edit_text(get_text("order_canceled", lang))
    await callback.answer()
