from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.brand_repo import get_brands_by_market
from bot.database.repository.category_repo import get_categories_by_market
from bot.database.repository.market_repo import get_all_markets
from bot.database.repository.product_repo import (
    get_product,
    get_products_by_brand,
    get_products_by_category,
    get_products_by_market,
    search_products,
)
from bot.keyboards.user_kb import (
    brands_filter_kb,
    categories_filter_kb,
    markets_kb,
    product_detail_kb,
    products_page_kb,
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
    for key in ("menu_shopping", "menu_cart", "menu_profile", "menu_settings", "menu_feedback")
    for lang in ("uz", "ru", "en")
) | frozenset(get_employe_text("admin_menu", lang) for lang in ("uz", "ru", "en"))
# Bitta sahifada nechta mahsulot ko'rsatilishi. 10 tadan ko'p bo'lsa,
# ◀️ 1/2 ▶️ ko'rinishidagi sahifalash (pagination) ishga tushadi.
PAGE_SIZE = 10


def _paginate(items: list, page: int) -> tuple[list, int, int]:
    """Ro'yxatni sahifalarga bo'ladi. Qaytaradi: (shu sahifadagi elementlar,
    to'g'irlangan sahifa raqami, jami sahifalar soni)."""
    total_pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    return items[start : start + PAGE_SIZE], page, total_pages


async def _get_filtered_products(
    session: AsyncSession, market_id: int, ftype: str, fid: int, state: FSMContext
) -> list:
    """`ftype` bo'yicha mos mahsulotlar ro'yxatini qaytaradi:
    "c" — kategoriya, "b" — brend, "s" — qidiruv natijasi (so'rov FSM
    state'da saqlanadi, chunki callback_data ichida erkin matn saqlab
    bo'lmaydi), aks holda ("a") — do'kondagi barcha mahsulotlar."""
    if ftype == "c":
        return await get_products_by_category(session, market_id, fid)
    if ftype == "b":
        return await get_products_by_brand(session, market_id, fid)
    if ftype == "s":
        data = await state.get_data()
        query = data.get("last_search_query", "")
        return await search_products(session, market_id, query)
    return await get_products_by_market(session, market_id)


async def _show_products(
    session: AsyncSession,
    lang: str,
    state: FSMContext,
    bot: Bot,
    send_target: Message,
    market_id: int,
    ftype: str,
    fid: int,
    page: int,
) -> None:
    """
    Mahsulotlar ro'yxatini (nomi — narxi tugmalari, rasmsiz, sahifalangan)
    ko'rsatadi. FSM state'da saqlangan "joriy mahsulotlar xabari"
    (products_chat_id/products_message_id) BOR bo'lsa — o'sha xabar
    TAHRIRLANADI (filtr yoki sahifa o'zgarganda ham yangi xabar
    yuborilmaydi). Agar hali bunday xabar bo'lmasa (yoki uni tahrirlab
    bo'lmasa — masalan o'chirilgan bo'lsa), `send_target` orqali yangi
    xabar yuboriladi va uning id'si state'ga yozib qo'yiladi.
    """
    products = await _get_filtered_products(session, market_id, ftype, fid, state)

    if not products:
        text = get_text("no_products", lang)
        keyboard = None
    else:
        page_products, page, total_pages = _paginate(products, page)
        keyboard = products_page_kb(page_products, market_id, ftype, fid, page, total_pages)
        text = get_text("search_hint", lang)

    data = await state.get_data()
    chat_id = data.get("products_chat_id")
    message_id = data.get("products_message_id")

    if chat_id and message_id:
        try:
            await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
            return
        except Exception:
            pass  # xabar topilmadi/tahrirlab bo'lmadi — pastda yangisini yuboramiz

    sent = await send_target.answer(text, reply_markup=keyboard)
    await state.update_data(products_chat_id=sent.chat.id, products_message_id=sent.message_id)


@router.message(F.text.func(lambda t: t in [get_text("menu_shopping", l) for l in ("uz", "ru", "en")]))
async def show_markets(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    await state.clear()
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_text("no_markets", lang))
        return
    await message.answer(get_text("choose_market", lang), reply_markup=markets_kb(markets))


@router.callback_query(F.data.startswith("market:"))
async def show_categories(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    """
    Do'kon tanlangandan keyin — shu ketma-ketlikda: 1) brendlar, 2)
    kategoriyalar, 3) mahsulotlar (rasmsiz, tugma ko'rinishida, sahifalangan)
    — to'g'ridan-to'g'ri, hech qanday oraliq tugmasiz chiqadi.
    """
    market_id = int(callback.data.split(":")[1])

    all_products = await get_products_by_market(session, market_id)
    if not all_products:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(get_text("market_empty", lang))
        await callback.answer()
        return
    
    # Yangi do'kon — avvalgi "joriy mahsulotlar xabari" iznini tozalaymiz,
    # shunda yangi ro'yxat albatta YANGI xabar sifatida yuboriladi.
    await state.set_data({})
    await state.update_data(market_id=market_id)
    await state.set_state(Shopping.searching_product)  # matn kelsa - qidiruv sifatida qaraladi

    try:
        await callback.message.delete()
    except Exception:
        pass

    brands = await get_brands_by_market(session, market_id)
    if brands:
        await callback.message.answer(
            get_text("choose_brand", lang), reply_markup=brands_filter_kb(brands, market_id, lang)
        )

    categories = await get_categories_by_market(session, market_id)
    if categories:
        await callback.message.answer(
            get_text("choose_category", lang), reply_markup=categories_filter_kb(categories, market_id, lang)
        )

    await _show_products(session, lang, state, bot, callback.message, market_id, "a", 0, 0)
    await callback.answer()


@router.callback_query(F.data.startswith("cat_filter:"))
async def filter_by_category(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    _, market_id, category_id = callback.data.split(":")
    market_id, category_id = int(market_id), int(category_id)
    await _show_products(session, lang, state, bot, callback.message, market_id, "c", category_id, 0)
    await callback.answer()


@router.callback_query(F.data.startswith("brand_filter:"))
async def filter_by_brand(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    _, market_id, brand_id = callback.data.split(":")
    market_id, brand_id = int(market_id), int(brand_id)
    await _show_products(session, lang, state, bot, callback.message, market_id, "b", brand_id, 0)
    await callback.answer()


@router.callback_query(F.data.startswith("prod_page:"))
async def paginate_products(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    """
    Sahifa almashtirish (◀️/▶️) — mahsulotlar xabari qayta yuborilmaydi,
    tahrirlanadi. Mahsulot tafsiloti sahifasidagi "orqaga" tugmasi ham shu
    handlerga keladi — bunday holda tafsilot xabari (rasm bilan) yopiladi
    va asosiy ro'yxat xabari o'sha sahifaga qaytariladi.
    """
    _, market_id, ftype, fid, page = callback.data.split(":")
    market_id, fid, page = int(market_id), int(fid), int(page)

    data = await state.get_data()
    tracked_message_id = data.get("products_message_id")
    if tracked_message_id and callback.message.message_id != tracked_message_id:
        # Bu chaqiruv mahsulot tafsiloti (rasmli) xabaridan "orqaga" bosilgani —
        # o'sha xabarni tozalaymiz, asosiy ro'yxat xabari alohida tahrirlanadi.
        try:
            await callback.message.delete()
        except Exception:
            pass

    await _show_products(session, lang, state, bot, callback.message, market_id, ftype, fid, page)
    await callback.answer()


@router.callback_query(F.data == "noop_page")
async def noop_page(callback: CallbackQuery):
    """Sahifa raqami ko'rsatkichi ("1/2") — bosilganda hech narsa qilmaydi."""
    await callback.answer()


@router.message(Shopping.searching_product, F.text, F.text.func(lambda t: t not in _RESERVED_MENU_TEXTS))
async def search_in_market(message: Message, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    data = await state.get_data()
    market_id = data.get("market_id")
    if not market_id:
        return  # holat mos kelmasa e'tiborsiz qoldiramiz

    query = message.text.strip()
    await state.update_data(last_search_query=query)
    await _show_products(session, lang, state, bot, message, market_id, "s", 0, 0)


@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, market_id, ftype, fid, page, product_id = callback.data.split(":")
    market_id, fid, page, product_id = int(market_id), int(fid), int(page), int(product_id)

    product = await get_product(session, product_id)
    if not product:
        await callback.answer(get_text("product_not_found", lang), show_alert=True)
        return

    text = (
        f"<b>{product.name}</b>\n\n"
        f"{product.discription or ''}\n\n"
        f"{get_text('product_price', lang)}: {product.price:,.0f}\n"
        f"{get_text('product_stock', lang)}: {product.stock}"
    )
    keyboard = product_detail_kb(product.id, 1, lang, market_id, ftype, fid, page)

    if product.image_file_id:
        await callback.message.answer_photo(product.image_file_id, caption=text, reply_markup=keyboard)
    else:
        await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("qty_inc:"))
async def quantity_increase(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, product_id, quantity, market_id, ftype, fid, page = callback.data.split(":")
    product_id, quantity, market_id, fid, page = (
        int(product_id), int(quantity), int(market_id), int(fid), int(page)
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
        reply_markup=product_detail_kb(product_id, new_quantity, lang, market_id, ftype, fid, page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qty_dec:"))
async def quantity_decrease(callback: CallbackQuery, lang: str):
    _, product_id, quantity, market_id, ftype, fid, page = callback.data.split(":")
    product_id, quantity, market_id, fid, page = (
        int(product_id), int(quantity), int(market_id), int(fid), int(page)
    )

    new_quantity = max(quantity - 1, 1)
    if new_quantity == quantity:
        await callback.answer()  # allaqachon eng past chegarada (1)
        return

    await callback.message.edit_reply_markup(
        reply_markup=product_detail_kb(product_id, new_quantity, lang, market_id, ftype, fid, page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qty_set:"))
async def quantity_start_manual_input(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    _, product_id, market_id, ftype, fid, page = callback.data.split(":")
    product_id, market_id, fid, page = int(product_id), int(market_id), int(fid), int(page)

    product = await get_product(session, product_id)
    if not product:
        await callback.answer(get_text("product_not_found", lang), show_alert=True)
        return

    # Mahsulot tafsiloti xabarini keyin (edit_message_reply_markup orqali)
    # yangilash uchun chat_id/message_id ni saqlab qo'yamiz.
    await state.update_data(
        qty_product_id=product_id,
        qty_market_id=market_id,
        qty_ftype=ftype,
        qty_fid=fid,
        qty_page=page,
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

    market_id = data.get("qty_market_id")
    ftype = data.get("qty_ftype")
    fid = data.get("qty_fid")
    page = data.get("qty_page")
    chat_id = data.get("qty_chat_id")
    message_id = data.get("qty_message_id")

    # Faqat vaqtinchalik "qty_*" ma'lumotlarini tozalaymiz, umumiy
    # (market_id, products_chat_id/message_id, last_search_query) holatni emas.
    await state.update_data(
        qty_product_id=None, qty_market_id=None, qty_ftype=None, qty_fid=None,
        qty_page=None, qty_chat_id=None, qty_message_id=None,
    )
    await state.set_state(Shopping.searching_product)

    try:
        await message.delete()
    except Exception:
        pass

    if not chat_id or not message_id:
        return

    keyboard = product_detail_kb(product_id, quantity, lang, market_id, ftype, fid, page)
    try:
        await message.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
    except Exception:
        pass


@router.callback_query(F.data.startswith("cart_add:"))
async def add_product_to_cart(callback: CallbackQuery, session: AsyncSession, lang: str):
    _, product_id, quantity = callback.data.split(":")
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
