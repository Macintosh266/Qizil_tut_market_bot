from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.brand_repo import (
    create_brand,
    get_all_brands,
    get_brand,
    get_brand_by_name,
)
from bot.database.repository.category_repo import (
    create_category,
    get_all_categories,
    get_category,
    get_category_by_name,
    get_or_create_category,
)
from bot.database.repository.market_repo import get_all_markets, get_market
from bot.database.repository.product_repo import (
    add_or_restock_product,
    delete_product,
    get_product,
    get_products_by_market,
    update_product_category,
    update_product_description,
    update_product_name,
    update_product_photo,
    update_product_price,
    update_product_stock,
)
from bot.enums.enum import UserRole
from bot.filters import IsAdmin
from bot.handlers.admin.base import CONFIRM_TEXTS, btn_texts, finish, track_list_message
from bot.keyboards.admin_kb import (
    brands_pick_kb,
    cancel_kb,
    categories_pick_kb,
    confirm_kb,
    market_choose_kb,
    markets_select_kb,
    product_edit_field_kb,
    product_list_kb,
    products_select_kb,
)
from bot.lexicons import get_employe_text, get_text
from bot.models import UserModel
from bot.states import AdminPanelStates

router = Router(name="admin_products")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ==================== MAHSULOT QO'SHISH — admin panel (tugmalar) ====================

@router.message(F.text.func(lambda t: t in btn_texts("add_product_btn")))
async def start_add_product(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    if db_user.role != UserRole.SUPER_ADMIN:
        # Do'konga bog'langan admin uchun do'kon tanlash shart emas
        await state.update_data(market_id=db_user.market_id)
        await state.set_state(AdminPanelStates.waiting_add_product_name)
        await message.answer(get_employe_text("add_product_name_prompt", lang), reply_markup=cancel_kb(lang))
        return

    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="ap_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "ap_market_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("ap_market_pick:"))
async def pick_add_product_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market.id)
    await state.set_state(AdminPanelStates.waiting_add_product_name)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(get_employe_text("add_product_name_prompt", lang), reply_markup=cancel_kb(lang))
    await callback.answer()


@router.message(AdminPanelStates.waiting_add_product_name, F.text)
async def process_add_product_name(message: Message, state: FSMContext, lang: str):
    await state.update_data(product_name=message.text.strip())
    await state.set_state(AdminPanelStates.waiting_add_product_qty)
    await message.answer(get_employe_text("add_product_qty_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_product_qty, F.text)
async def process_add_product_qty(message: Message, state: FSMContext, lang: str):
    if not message.text.strip().isdigit():
        await message.answer(get_employe_text("only_numbers", lang))
        return
    await state.update_data(quantity=int(message.text.strip()))
    await state.set_state(AdminPanelStates.waiting_add_product_price)
    await message.answer(get_employe_text("add_product_price_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_product_price, F.text)
async def process_add_product_price(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    try:
        price = float(message.text.strip())
    except ValueError:
        await message.answer(get_employe_text("only_numbers", lang))
        return
    await state.update_data(price=price)
    await _ask_choose_brand(message, session, lang)


async def _ask_choose_brand(target: Message, session: AsyncSession, lang: str) -> None:
    brands = await get_all_brands(session)
    await target.answer(
        get_employe_text("choose_brand_prompt", lang),
        reply_markup=brands_pick_kb(brands, "apb_pick", lang),
    )


@router.callback_query(F.data.startswith("apb_pick:"))
async def pick_add_product_brand(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    value = callback.data.split(":", 1)[1]

    if value == "new":
        await state.set_state(AdminPanelStates.waiting_new_brand_inline)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(get_employe_text("add_brand_prompt", lang), reply_markup=cancel_kb(lang))
        await callback.answer()
        return

    if value == "none":
        await state.update_data(brand_id=None)
    else:
        brand = await get_brand(session, int(value))
        if not brand:
            await callback.answer(get_employe_text("no_brands", lang), show_alert=True)
            return
        await state.update_data(brand_id=brand.id)

    try:
        await callback.message.delete()
    except Exception:
        pass
    await _ask_choose_category(callback.message, session, lang)
    await callback.answer()


@router.message(AdminPanelStates.waiting_new_brand_inline, F.text)
async def process_new_brand_inline(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    name = message.text.strip()
    brand = await get_brand_by_name(session, name)
    if not brand:
        brand = await create_brand(session, name)
    await state.update_data(brand_id=brand.id)
    await _ask_choose_category(message, session, lang)


async def _ask_choose_category(target: Message, session: AsyncSession, lang: str) -> None:
    categories = await get_all_categories(session)
    await target.answer(
        get_employe_text("choose_category_prompt", lang),
        reply_markup=categories_pick_kb(categories, "apc_pick", lang),
    )


@router.callback_query(F.data.startswith("apc_pick:"))
async def pick_add_product_category(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    value = callback.data.split(":", 1)[1]

    if value == "new":
        await state.set_state(AdminPanelStates.waiting_new_category_inline)
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(get_employe_text("add_category_prompt", lang), reply_markup=cancel_kb(lang))
        await callback.answer()
        return

    category = await get_category(session, int(value))
    if not category:
        await callback.answer(get_employe_text("no_categories", lang), show_alert=True)
        return

    await state.update_data(category_id=category.id)
    await state.set_state(AdminPanelStates.waiting_add_product_photo)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(get_employe_text("add_product_photo_prompt", lang), reply_markup=cancel_kb(lang))
    await callback.answer()


@router.message(AdminPanelStates.waiting_new_category_inline, F.text)
async def process_new_category_inline(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    name = message.text.strip()
    category = await get_category_by_name(session, name)
    if not category:
        category = await create_category(session, name)
    await state.update_data(category_id=category.id)
    await state.set_state(AdminPanelStates.waiting_add_product_photo)
    await message.answer(get_employe_text("add_product_photo_prompt", lang), reply_markup=cancel_kb(lang))


async def _create_product_and_finish(
    message: Message, session: AsyncSession, lang: str, state: FSMContext, image_file_id: str | None
) -> None:
    data = await state.get_data()
    product, created = await add_or_restock_product(
        session,
        market_id=data["market_id"],
        category_id=data["category_id"],
        name=data["product_name"],
        price=data["price"],
        stock_to_add=data["quantity"],
        image_file_id=image_file_id,
        brand_id=data.get("brand_id"),
    )

    if created:
        text = get_employe_text("product_added", lang, name=product.name, price=f"{product.price:,.0f}")
    else:
        text = get_employe_text(
            "product_restocked", lang, name=product.name, stock=data["quantity"], total=product.stock
        )

    await finish(message, state, lang, text)


@router.message(AdminPanelStates.waiting_add_product_photo, F.photo)
async def process_add_product_photo(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    file_id = message.photo[-1].file_id
    await _create_product_and_finish(message, session, lang, state, file_id)


@router.message(AdminPanelStates.waiting_add_product_photo, F.text == "-")
async def skip_add_product_photo(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    await _create_product_and_finish(message, session, lang, state, None)


# ==================== MAHSULOT O'CHIRISH — admin panel (tugmalar) ====================

@router.message(F.text.func(lambda t: t in btn_texts("delete_product_btn")))
async def start_delete_product(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    if db_user.role != UserRole.SUPER_ADMIN:
        products = await get_products_by_market(session, db_user.market_id)
        if not products:
            await message.answer(get_employe_text("empty_list", lang))
            return
        await state.update_data(market_id=db_user.market_id, search_context="dp_product")
        await state.set_state(AdminPanelStates.searching_product)
        sent = await message.answer(
            get_employe_text("choose_product_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
            reply_markup=products_select_kb(products, "dp_product_pick", lang),
        )
        await track_list_message(state, sent)
        return

    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="dp_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "dp_market_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("dp_market_pick:"))
async def pick_delete_product_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    products = await get_products_by_market(session, market_id)
    if not products:
        await callback.answer(get_employe_text("empty_list", lang), show_alert=True)
        return
    await state.update_data(market_id=market_id, search_context="dp_product")
    await state.set_state(AdminPanelStates.searching_product)
    await callback.message.edit_text(
        get_employe_text("choose_product_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=products_select_kb(products, "dp_product_pick", lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("dp_product_pick:"))
async def pick_delete_product(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    product = await get_product(session, product_id)
    if not product:
        await callback.answer(get_employe_text("product_not_found", lang), show_alert=True)
        return
    await state.update_data(product_id=product.id)
    await state.set_state(AdminPanelStates.waiting_confirm_delete_product)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_employe_text("confirm_delete_product", lang, name=product.name), reply_markup=confirm_kb(lang)
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_confirm_delete_product, F.text.func(lambda t: t in CONFIRM_TEXTS))
async def process_confirm_delete_product(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if product:
        await delete_product(session, product)
    await finish(
        message, state, lang, get_employe_text("product_deleted", lang, name=product.name if product else "")
    )


# ==================== MAHSULOTNI TAHRIRLASH (nomi, tavsifi, narxi, miqdori, kategoriyasi, rasmi) ====================

@router.message(F.text.func(lambda t: t in btn_texts("edit_product_price_btn")))
async def start_edit_product(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    if db_user.role != UserRole.SUPER_ADMIN:
        products = await get_products_by_market(session, db_user.market_id)
        if not products:
            await message.answer(get_employe_text("empty_list", lang))
            return
        await state.update_data(market_id=db_user.market_id, search_context="ep_product")
        await state.set_state(AdminPanelStates.searching_product)
        sent = await message.answer(
            get_employe_text("choose_product_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
            reply_markup=products_select_kb(products, "ep_product_pick", lang),
        )
        await track_list_message(state, sent)
        return

    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="ep_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "ep_market_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(F.data.startswith("ep_market_pick:"))
async def pick_edit_product_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    products = await get_products_by_market(session, market_id)
    if not products:
        await callback.answer(get_employe_text("empty_list", lang), show_alert=True)
        return
    await state.update_data(market_id=market_id, search_context="ep_product")
    await state.set_state(AdminPanelStates.searching_product)
    await callback.message.edit_text(
        get_employe_text("choose_product_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=products_select_kb(products, "ep_product_pick", lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ep_product_pick:"))
async def pick_edit_product(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    product = await get_product(session, product_id)
    if not product:
        await callback.answer(get_employe_text("product_not_found", lang), show_alert=True)
        return
    await state.set_state(None)
    await callback.message.edit_text(
        f"<b>{product.name}</b>\n\n" + get_employe_text("choose_field_to_edit", lang),
        reply_markup=product_edit_field_kb(product.id, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_field:"))
async def choose_edit_field(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    _, field, product_id = callback.data.split(":")
    product = await get_product(session, int(product_id))
    if not product:
        await callback.answer(get_employe_text("product_not_found", lang), show_alert=True)
        return

    field_state = {
        "name": AdminPanelStates.waiting_edit_name_value,
        "description": AdminPanelStates.waiting_edit_description_value,
        "price": AdminPanelStates.waiting_edit_price_new_value,
        "stock": AdminPanelStates.waiting_edit_stock_value,
        "category": AdminPanelStates.waiting_edit_category_value,
        "photo": AdminPanelStates.waiting_edit_photo_value,
    }
    field_prompt = {
        "name": "edit_new_name_prompt",
        "description": "edit_new_description_prompt",
        "price": "edit_product_new_price_prompt",
        "stock": "edit_new_stock_prompt",
        "category": "edit_new_category_prompt",
        "photo": "edit_new_photo_prompt",
    }

    await state.update_data(product_id=product.id)
    await state.set_state(field_state[field])
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        f"<b>{product.name}</b>\n\n" + get_employe_text(field_prompt[field], lang),
        reply_markup=cancel_kb(lang),
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_edit_name_value, F.text)
async def process_edit_name(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await finish(message, state, lang, get_employe_text("product_not_found", lang))
        return
    new_name = message.text.strip()
    await update_product_name(session, product, new_name)
    await finish(message, state, lang, get_employe_text("product_name_updated", lang, name=new_name))


@router.message(AdminPanelStates.waiting_edit_description_value, F.text)
async def process_edit_description(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await finish(message, state, lang, get_employe_text("product_not_found", lang))
        return
    await update_product_description(session, product, message.text.strip())
    await finish(message, state, lang, get_employe_text("product_description_updated", lang))


@router.message(AdminPanelStates.waiting_edit_price_new_value, F.text)
async def process_edit_price_new_value(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    try:
        new_price = float(message.text.strip())
    except ValueError:
        await message.answer(get_employe_text("only_numbers", lang))
        return

    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    await update_product_price(session, product, new_price)
    await finish(
        message, state, lang,
        get_employe_text("product_price_updated", lang, name=product.name, price=f"{new_price:,.0f}"),
    )


@router.message(AdminPanelStates.waiting_edit_stock_value, F.text)
async def process_edit_stock(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer(get_employe_text("only_numbers", lang))
        return

    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    new_stock = max(0, int(message.text.strip()))
    await update_product_stock(session, product, new_stock)
    await finish(message, state, lang, get_employe_text("product_stock_updated", lang, stock=new_stock))


@router.message(AdminPanelStates.waiting_edit_category_value, F.text)
async def process_edit_category(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    category_name = message.text.strip()
    category = await get_or_create_category(session, category_name)
    await update_product_category(session, product, category.id)
    await finish(message, state, lang, get_employe_text("product_category_updated", lang, name=category_name))


@router.message(AdminPanelStates.waiting_edit_photo_value, F.photo)
async def process_edit_photo(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    file_id = message.photo[-1].file_id
    await update_product_photo(session, product, file_id)
    await finish(message, state, lang, get_employe_text("product_photo_updated", lang))


# ==================== MAHSULOTLAR RO'YXATI (do'kon tanlash orqali) ====================

@router.message(F.text.func(lambda t: t in btn_texts("product_list_btn")))
async def ask_product_list_market(message: Message, session: AsyncSession, lang: str, db_user: UserModel):
    if db_user.role != UserRole.SUPER_ADMIN:
        products = await get_products_by_market(session, db_user.market_id)
        if not products:
            await message.answer(get_employe_text("empty_list", lang))
            return
        await message.answer(
            get_employe_text("product_list_btn", lang), reply_markup=product_list_kb(products, lang)
        )
        return

    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await message.answer(get_text("choose_market", lang), reply_markup=market_choose_kb(markets, lang))


@router.callback_query(F.data.startswith("market_choose:"))
async def show_market_products(callback: CallbackQuery, session: AsyncSession, lang: str):
    market_id = int(callback.data.split(":")[1])
    products = await get_products_by_market(session, market_id)
    if not products:
        await callback.message.edit_text(get_employe_text("empty_list", lang))
        await callback.answer()
        return
    await callback.message.edit_text(
        get_employe_text("product_list_btn", lang), reply_markup=product_list_kb(products, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_info:"))
async def show_product_info(callback: CallbackQuery, session: AsyncSession, lang: str):
    product_id = int(callback.data.split(":")[1])
    product = await get_product(session, product_id)
    if not product:
        await callback.answer()
        return
    text = (
        f"<b>{product.name}</b>\n"
        f"{get_text('product_price', lang)}: {product.price:,.0f}\n"
        f"{get_text('product_stock', lang)}: {product.stock}"
    )
    if product.image_file_id:
        await callback.message.answer_photo(product.image_file_id, caption=text)
    else:
        await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "back_to_admin")
async def close_inline_list(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()