from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.product_repo import get_product
from bot.lexicons import get_text
from bot.keyboards.user_kb import cart_kb
from bot.redis import get_cart, remove_from_cart, set_cart_item
from bot.states import Cart

router = Router(name="cart")


async def _build_cart_view(session: AsyncSession, user_id: int):
    cart = await get_cart(user_id)
    items, total = [], 0.0

    for product_id, quantity in cart.items():
        product = await get_product(session, product_id)
        if not product:
            continue
        subtotal = float(product.price) * quantity
        total += subtotal
        items.append(
            {
                "product_id": product_id,
                "name": product.name,
                "price": float(product.price),
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )
    return items, total


def _cart_text(items: list[dict], total: float, lang: str) -> str:
    lines = [f"{i['name']} — {i['quantity']} x {i['price']:,.0f} = {i['subtotal']:,.0f}" for i in items]
    return (
        get_text("cart_title", lang)
        + "\n\n"
        + "\n".join(lines)
        + f"\n\n{get_text('cart_total', lang)}: {total:,.0f}"
    )


@router.message(F.text.func(lambda t: t in [get_text("menu_cart", l) for l in ("uz", "ru", "en")]))
async def show_cart(message: Message, session: AsyncSession, lang: str):
    items, total = await _build_cart_view(session, message.from_user.id)
    if not items:
        await message.answer(get_text("cart_empty", lang))
        return
    await message.answer(_cart_text(items, total, lang), reply_markup=cart_kb(items, lang))


@router.callback_query(F.data.startswith("cart_inc:"))
async def cart_increase(callback: CallbackQuery, session: AsyncSession, lang: str):
    product_id = int(callback.data.split(":")[1])
    cart = await get_cart(callback.from_user.id)
    await set_cart_item(callback.from_user.id, product_id, cart.get(product_id, 0) + 1)
    await _refresh(callback, session, lang)


@router.callback_query(F.data.startswith("cart_dec:"))
async def cart_decrease(callback: CallbackQuery, session: AsyncSession, lang: str):
    product_id = int(callback.data.split(":")[1])
    cart = await get_cart(callback.from_user.id)
    await set_cart_item(callback.from_user.id, product_id, cart.get(product_id, 0) - 1)
    await _refresh(callback, session, lang)


@router.callback_query(F.data.startswith("cart_del:"))
async def cart_delete(callback: CallbackQuery, session: AsyncSession, lang: str):
    product_id = int(callback.data.split(":")[1])
    await remove_from_cart(callback.from_user.id, product_id)
    await _refresh(callback, session, lang)


@router.callback_query(F.data.startswith("cart_qty:"))
async def cart_start_edit_quantity(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    product = await get_product(session, product_id)
    if not product:
        await callback.answer(get_text("product_not_found", lang), show_alert=True)
        return

    # Savat xabari (tugmalar bilan) qayerda joylashganini eslab qolamiz, chunki
    # foydalanuvchi sonni yozib yuborgach, aynan shu xabarni yangilaymiz.
    await state.update_data(
        cart_product_id=product_id,
        cart_chat_id=callback.message.chat.id,
        cart_message_id=callback.message.message_id,
    )
    await state.set_state(Cart.waiting_quantity)
    await callback.message.answer(get_text("cart_qty_prompt", lang, name=product.name))
    await callback.answer()


@router.message(Cart.waiting_quantity, F.text)
async def cart_process_new_quantity(message: Message, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer(get_text("only_numbers", lang))
        return

    data = await state.get_data()
    product_id = data.get("cart_product_id")
    product = await get_product(session, product_id) if product_id else None
    if not product:
        await state.clear()
        await message.answer(get_text("product_not_found", lang))
        return

    quantity = max(0, int(message.text.strip()))
    if quantity > product.stock:
        await message.answer(get_text("not_enough_stock", lang, stock=product.stock))
        return

    await set_cart_item(message.from_user.id, product_id, quantity)
    await state.clear()

    # Foydalanuvchi yuborgan xabarni tozalab, asosiy savat xabarini yangilaymiz
    try:
        await message.delete()
    except Exception:
        pass

    items, total = await _build_cart_view(session, message.from_user.id)
    chat_id, message_id = data.get("cart_chat_id"), data.get("cart_message_id")
    if not chat_id or not message_id:
        return

    try:
        if not items:
            await bot.edit_message_text(get_text("cart_empty", lang), chat_id=chat_id, message_id=message_id)
        else:
            await bot.edit_message_text(
                _cart_text(items, total, lang),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=cart_kb(items, lang),
            )
    except Exception:
        pass


async def _refresh(callback: CallbackQuery, session: AsyncSession, lang: str):
    items, total = await _build_cart_view(session, callback.from_user.id)
    if not items:
        await callback.message.edit_text(get_text("cart_empty", lang))
        await callback.answer()
        return
    await callback.message.edit_text(_cart_text(items, total, lang), reply_markup=cart_kb(items, lang))
    await callback.answer()