from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.product_repo import get_product
from bot.lexicons import get_text
from bot.keyboards.user_kb import cart_kb
from bot.redis import get_cart, remove_from_cart, set_cart_item

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


async def _refresh(callback: CallbackQuery, session: AsyncSession, lang: str):
    items, total = await _build_cart_view(session, callback.from_user.id)
    if not items:
        await callback.message.edit_text(get_text("cart_empty", lang))
        await callback.answer()
        return
    await callback.message.edit_text(_cart_text(items, total, lang), reply_markup=cart_kb(items, lang))
    await callback.answer()
