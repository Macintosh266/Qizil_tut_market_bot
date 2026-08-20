from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.category_repo import get_categories_by_market
from bot.database.repository.market_repo import get_all_markets
from bot.database.repository.product_repo import (
    get_product,
    get_products_by_category,
    get_products_by_market,
    search_products,
)
from bot.keyboards.user_kb import (
    categories_kb,
    markets_kb,
    product_detail_kb,
    products_kb,
)
from bot.lexicons import get_text
from bot.lexicons.lexicon_employe import get_employe_text
from bot.redis import add_to_cart
from bot.states import Shopping

router = Router(name="shopping")

# Asosiy menyu tugmalarining matni — foydalanuvchi biror holatda (masalan
# Shopping.searching_product) bo'lganda ham, shu tugmalardan birini bossa,
# bu matn qidiruv so'rovi sifatida QABUL QILINMASLIGI kerak.
_RESERVED_MENU_TEXTS = frozenset(
    get_text(key, lang)
    for key in ("menu_shopping", "menu_cart", "menu_profile", "menu_settings")
    for lang in ("uz", "ru", "en")
) | frozenset(get_employe_text("admin_menu", lang) for lang in ("uz", "ru", "en"))

# Qidiruv natijalari turli kategoriyalardan kelishi mumkin bo'lgani uchun,
# bunday holatda category_id sifatida shu "sentinel" qiymat ishlatiladi —
# "orqaga qaytish" tugmasi bosilganda kategoriyalar ro'yxatiga qaytariladi.
_SEARCH_CATEGORY_SENTINEL = 0


@router.message(F.text.func(lambda t: t in [get_text("menu_shopping", l) for l in ("uz", "ru", "en")]))
async def show_markets(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    await state.clear()
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_text("no_markets", lang))
        return
    await message.answer(get_text("choose_market", lang), reply_markup=markets_kb(markets))


@router.callback_query(F.data.startswith("market:"))
async def show_categories(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    await state.update_data(market_id=market_id)
    categories = await get_categories_by_market(session, market_id)

    if not categories:
        # Kategoriya bo'lmasa ham, do'konda mahsulot bo'lishi mumkin —
        # to'g'ridan-to'g'ri barcha mahsulotlarni ko'rsatamiz
        await show_all_products(callback, session, lang, state)
        return

    await callback.message.edit_text(
        get_text("choose_category", lang) + get_text("search_hint", lang),
        reply_markup=categories_kb(categories, market_id, lang),
    )
    await state.set_state(Shopping.searching_product)  # matn kelsa - qidiruv sifatida qaraladi
    await callback.answer()


@router.callback_query(F.data == "back_to_markets")
async def back_to_markets(callback: CallbackQuery, session: AsyncSession, lang: str):
    markets = await get_all_markets(session)
    await callback.message.edit_text(get_text("choose_market", lang), reply_markup=markets_kb(markets))
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_categories:"))
async def back_to_categories(callback: CallbackQuery, session: AsyncSession, lang: str):
    market_id = int(callback.data.split(":")[1])
    categories = await get_categories_by_market(session, market_id)
    await callback.message.edit_text(
        get_text("choose_category", lang) + get_text("search_hint", lang),
        reply_markup=categories_kb(categories, market_id, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("all_products:"))
async def show_all_products(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    await state.update_data(market_id=market_id)
    products = await get_products_by_market(session, market_id)

    if not products:
        await callback.answer(get_text("no_products", lang), show_alert=True)
        return

    await callback.message.edit_text(
        get_text("search_hint", lang), reply_markup=products_kb(products, market_id, _SEARCH_CATEGORY_SENTINEL)
    )
    await state.set_state(Shopping.searching_product)
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_products(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, market_id, category_id = callback.data.split(":")
    market_id, category_id = int(market_id), int(category_id)
    products = await get_products_by_category(session, market_id, category_id)

    if not products:
        await callback.answer(get_text("no_products", lang), show_alert=True)
        return

    await callback.message.edit_text(
        get_text("search_hint", lang), reply_markup=products_kb(products, market_id, category_id)
    )
    await callback.answer()


@router.message(Shopping.searching_product, F.text, F.text.func(lambda t: t not in _RESERVED_MENU_TEXTS))
async def search_in_market(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    market_id = data.get("market_id")
    if not market_id:
        return  # holat mos kelmasa e'tiborsiz qoldiramiz

    products = await search_products(session, market_id, message.text.strip())
    if not products:
        await message.answer(get_text("no_products", lang))
        return

    await message.answer(
        get_text("search_hint", lang),
        reply_markup=products_kb(products, market_id, _SEARCH_CATEGORY_SENTINEL),
    )


@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, market_id, category_id, product_id = callback.data.split(":")
    market_id, category_id, product_id = int(market_id), int(category_id), int(product_id)

    product = await get_product(session, product_id)
    if not product:
        await callback.answer("Not found", show_alert=True)
        return

    text = (
        f"<b>{product.name}</b>\n\n"
        f"{product.discription or ''}\n\n"
        f"{get_text('product_price', lang)}: {product.price:,.0f}\n"
        f"{get_text('product_stock', lang)}: {product.stock}"
    )
    keyboard = product_detail_kb(product.id, 1, lang, market_id, category_id)

    if product.image_file_id:
        await callback.message.answer_photo(product.image_file_id, caption=text, reply_markup=keyboard)
    else:
        await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("qty_inc:"))
async def quantity_increase(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, market_id, category_id, product_id, quantity = callback.data.split(":")
    market_id, category_id, product_id, quantity = (
        int(market_id), int(category_id), int(product_id), int(quantity)
    )

    product = await get_product(session, product_id)
    if not product or product.stock <= 0:
        await callback.answer()
        return

    new_quantity = min(quantity + 1, product.stock)
    if new_quantity == quantity:
        await callback.answer()  # allaqachon eng yuqori chegarada
        return

    await callback.message.edit_reply_markup(
        reply_markup=product_detail_kb(product_id, new_quantity, lang, market_id, category_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qty_dec:"))
async def quantity_decrease(callback: CallbackQuery, lang: str):
    _, market_id, category_id, product_id, quantity = callback.data.split(":")
    market_id, category_id, product_id, quantity = (
        int(market_id), int(category_id), int(product_id), int(quantity)
    )

    new_quantity = max(quantity - 1, 1)
    if new_quantity == quantity:
        await callback.answer()  # allaqachon eng past chegarada (1)
        return

    await callback.message.edit_reply_markup(
        reply_markup=product_detail_kb(product_id, new_quantity, lang, market_id, category_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("qty_set:"))
async def quantity_start_manual_input(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    _, market_id, category_id, product_id = callback.data.split(":")
    market_id, category_id, product_id = int(market_id), int(category_id), int(product_id)

    product = await get_product(session, product_id)
    if not product:
        await callback.answer(get_text("product_not_found", lang), show_alert=True)
        return

    # Mahsulot tafsiloti xabarini keyin (edit_message_reply_markup orqali)
    # yangilash uchun chat_id/message_id ni saqlab qo'yamiz.
    await state.update_data(
        qty_market_id=market_id,
        qty_category_id=category_id,
        qty_product_id=product_id,
        qty_chat_id=callback.message.chat.id,
        qty_message_id=callback.message.message_id,
    )
    await state.set_state(Shopping.waiting_quantity)
    await callback.message.answer(get_text("product_qty_prompt", lang, name=product.name))
    await callback.answer()


@router.message(Shopping.waiting_quantity, F.text, F.text.func(lambda t: t not in _RESERVED_MENU_TEXTS))
async def process_manual_quantity(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer(get_text("only_numbers", lang))
        return
 
    data = await state.get_data()
    product_id = data.get("qty_product_id")
    product = await get_product(session, product_id) if product_id else None
    if not product:
        await state.clear()
        await message.answer(get_text("product_not_found", lang))
        return
 
    quantity = max(1, int(message.text.strip()))
    if quantity > product.stock:
        await message.answer(get_text("not_enough_stock", lang, stock=product.stock))
        return
 
    await state.clear()
 
    try:
        await message.delete()
    except Exception:
        pass
 
    market_id, category_id = data.get("qty_market_id"), data.get("qty_category_id")
    chat_id, message_id = data.get("qty_chat_id"), data.get("qty_message_id")
    if not chat_id or not message_id:
        return
 
    keyboard = product_detail_kb(product_id, quantity, lang, market_id, category_id)
    try:
        await message.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
    except Exception:
        pass

@router.callback_query(F.data.startswith("cart_add:"))
async def add_product_to_cart(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, market_id, category_id, product_id, quantity = callback.data.split(":")
    product_id, quantity = int(product_id), int(quantity)

    product = await get_product(session, product_id)
    if not product:
        await callback.answer()
        return

    if quantity > product.stock:
        await callback.answer(get_text("not_enough_stock", lang, stock=product.stock), show_alert=True)
        return

    await add_to_cart(callback.from_user.id, product_id, quantity)
    await callback.answer(get_text("added_to_cart", lang))


@router.callback_query(F.data.startswith("back_to_products:"))
async def back_to_products(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, market_id, category_id = callback.data.split(":")
    market_id, category_id = int(market_id), int(category_id)

    try:
        await callback.message.delete()
    except Exception:
        pass

    if category_id == _SEARCH_CATEGORY_SENTINEL:
        categories = await get_categories_by_market(session, market_id)
        await callback.message.answer(
            get_text("choose_category", lang) + get_text("search_hint", lang),
            reply_markup=categories_kb(categories, market_id, lang),
        )
    else:
        products = await get_products_by_category(session, market_id, category_id)
        await callback.message.answer(
            get_text("search_hint", lang), reply_markup=products_kb(products, market_id, category_id)
        )
    await callback.answer()