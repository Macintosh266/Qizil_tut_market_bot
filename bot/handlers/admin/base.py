"""
Admin panelning umumiy (barcha bo'limlarga tegishli) qismi:
- navigatsiya (asosiy menyu, submenyular, orqaga)
- bekor qilish handlerlari
- ro'yxat uzun bo'lganda yozib qidirish
- boshqa fayllar (admins.py, staff.py, ban.py, markets.py, products.py,
  statistics.py) foydalanadigan umumiy yordamchi funksiyalar va konstantalar
"""

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.market_repo import get_all_markets
from bot.database.repository.product_repo import get_products_by_market
from bot.database.repository.user_repo import list_admins, list_banned_users, list_staff
from bot.enums.enum import UserRole
from bot.filters import IsAdmin, IsSuperAdmin
from bot.keyboards.admin_kb import (
    admin_management_kb,
    admin_panel_kb,
    ban_management_kb,
    market_admin_panel_kb,
    market_management_kb,
    markets_select_kb,
    product_management_kb,
    products_select_kb,
    staff_management_kb,
    statistic_period_kb,
    users_select_kb,
)
from bot.keyboards.user_kb import main_menu_kb
from bot.lexicons import get_employe_text
from bot.models import UserModel
from bot.states import AdminPanelStates

router = Router(name="admin_base")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

# ==================== KONSTANTALAR (boshqa fayllar ham import qiladi) ====================

_ALL_WAITING_STATES = [
    AdminPanelStates.waiting_add_admin_id,
    AdminPanelStates.waiting_delete_admin_id,
    AdminPanelStates.waiting_add_staff_id,
    AdminPanelStates.waiting_delete_staff_id,
    AdminPanelStates.waiting_ban_id,
    AdminPanelStates.waiting_unban_id,
    AdminPanelStates.waiting_add_market_name,
    AdminPanelStates.waiting_add_market_address,
    AdminPanelStates.waiting_delete_market_name,
    AdminPanelStates.waiting_confirm_delete_market,
    AdminPanelStates.waiting_add_product_market,
    AdminPanelStates.waiting_add_product_name,
    AdminPanelStates.waiting_add_product_qty,
    AdminPanelStates.waiting_add_product_price,
    AdminPanelStates.waiting_add_product_category,
    AdminPanelStates.waiting_add_product_photo,
    AdminPanelStates.waiting_delete_product_market,
    AdminPanelStates.waiting_delete_product_name,
    AdminPanelStates.waiting_confirm_delete_product,
    AdminPanelStates.waiting_edit_price_market,
    AdminPanelStates.waiting_edit_price_product,
    AdminPanelStates.waiting_edit_price_new_value,
    AdminPanelStates.waiting_edit_name_value,
    AdminPanelStates.waiting_edit_description_value,
    AdminPanelStates.waiting_edit_stock_value,
    AdminPanelStates.waiting_edit_category_value,
    AdminPanelStates.waiting_edit_photo_value,
    AdminPanelStates.searching_market,
    AdminPanelStates.searching_product,
    AdminPanelStates.searching_user,
    AdminPanelStates.waiting_statistic_period,
]

CANCEL_TEXTS = frozenset(get_employe_text("cancel_btn", l) for l in ("uz", "ru", "en"))
CONFIRM_TEXTS = frozenset(get_employe_text("confirm_btn", l) for l in ("uz", "ru", "en"))

# Admin panelning BARCHA tugma matnlari (uch tilda) — qidiruv holatida bo'lsa
# ham, bu matnlar hech qachon "qidiruv so'rovi" sifatida qabul qilinmasligi
# kerak, aks holda masalan "📋 Adminlar ro'yxati" tugmasi bosilganda u ism
# bo'yicha qidiruv deb tushunilib, "Hech narsa topilmadi" xatosi chiqadi.
_ALL_ADMIN_BUTTON_KEYS = [
    "admin_menu", "admin_management_btn", "staff_management_btn", "ban_management_btn",
    "market_management_btn", "product_management_btn", "statistics_btn", "back_btn",
    "add_admin_btn", "delete_admin_btn", "admin_list_btn",
    "add_staff_btn", "delete_staff_btn", "staff_list_btn",
    "ban_user_btn", "unban_user_btn",
    "add_market_btn", "delete_market_btn", "market_list_btn",
    "add_product_btn", "delete_product_btn", "product_list_btn", "edit_product_price_btn",
    "confirm_btn", "cancel_btn",
]
ALL_ADMIN_BUTTON_TEXTS = frozenset(
    get_employe_text(key, l) for key in _ALL_ADMIN_BUTTON_KEYS for l in ("uz", "ru", "en")
)

MARKET_SEARCH_PREFIXES = {
    "del_market": "del_market_pick",
    "ap_market": "ap_market_pick",
    "dp_market": "dp_market_pick",
    "ep_market": "ep_market_pick",
    "aa_market": "aa_market_pick",
    "as_market": "as_market_pick",
}
PRODUCT_SEARCH_PREFIXES = {
    "dp_product": "dp_product_pick",
    "ep_product": "ep_product_pick",
}
USER_SEARCH_CONFIG = {
    "da_user": ("choose_admin_prompt", "da_pick", list_admins),
    "ds_user": ("choose_staff_prompt", "ds_pick", list_staff),
    "un_user": ("choose_banned_prompt", "un_pick", list_banned_users),
}


# ==================== YORDAMCHI FUNKSIYALAR (boshqa fayllar ham import qiladi) ====================

def btn_texts(key: str) -> frozenset:
    return frozenset(get_employe_text(key, l) for l in ("uz", "ru", "en"))


def kb_for_level(level: str, lang: str, is_super_admin: bool = False):
    mapping = {
        "admin_mgmt": admin_management_kb,
        "staff_mgmt": staff_management_kb,
        "ban_mgmt": ban_management_kb,
        "market_mgmt": market_management_kb,
        "product_mgmt": product_management_kb,
    }
    if level in mapping:
        return mapping[level](lang)
    return (admin_panel_kb if is_super_admin else market_admin_panel_kb)(lang)


async def finish(message: Message, state: FSMContext, lang: str, text: str) -> None:
    await clear_tracked_list(message.bot, state)
    data = await state.get_data()
    level = data.get("menu_level", "root")
    is_super_admin = data.get("is_super_admin", False)
    await state.set_state(None)
    await message.answer(text, reply_markup=kb_for_level(level, lang, is_super_admin))


async def finish_cb(callback: CallbackQuery, state: FSMContext, lang: str, text: str) -> None:
    await clear_tracked_list(callback.bot, state)
    data = await state.get_data()
    level = data.get("menu_level", "root")
    is_super_admin = data.get("is_super_admin", False)
    await state.set_state(None)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(text, reply_markup=kb_for_level(level, lang, is_super_admin))
    await callback.answer()


async def track_list_message(state: FSMContext, message: Message) -> None:
    """Ro'yxat (tanlash) xabarini FSM data'da eslab qolamiz — keyinroq yozib
    qidirilganda yoki jarayon tugaganda shu eski xabarni o'chirib tashlash uchun."""
    await state.update_data(list_msg_id=message.message_id, list_chat_id=message.chat.id)


async def clear_tracked_list(bot: Bot, state: FSMContext) -> None:
    """Eslab qolingan (eskirgan) ro'yxat xabarini, agar bo'lsa, o'chiradi."""
    data = await state.get_data()
    msg_id, chat_id = data.get("list_msg_id"), data.get("list_chat_id")
    if msg_id and chat_id:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception:
            pass
        await state.update_data(list_msg_id=None, list_chat_id=None)


# ==================== NAVIGATSIYA ====================
# Diqqat: har bir navigatsiya handleri FSM *holatini* ham tozalaydi
# (state.set_state(None)), aks holda oldingi bosqichda qolib ketgan
# holat (masalan "qidirish" yoki "yangi nom kutish") keyingi menyu
# tugmalarini ham "noto'g'ri kiritilgan qiymat" deb tushunib qolishi mumkin.

@router.message(F.text.func(lambda t: t in btn_texts("admin_menu")))
async def show_admin_panel(message: Message, state: FSMContext, lang: str, db_user: UserModel):
    is_super_admin = db_user.role == UserRole.SUPER_ADMIN
    await state.set_state(None)
    await state.update_data(menu_level="root", is_super_admin=is_super_admin)
    kb = admin_panel_kb(lang) if is_super_admin else market_admin_panel_kb(lang)
    await message.answer(get_employe_text("admin_panel_welcome", lang), reply_markup=kb)


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("admin_management_btn")))
async def open_admin_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="admin_mgmt")
    await message.answer(get_employe_text("admin_management_btn", lang), reply_markup=admin_management_kb(lang))


@router.message(F.text.func(lambda t: t in btn_texts("staff_management_btn")))
async def open_staff_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="staff_mgmt")
    await message.answer(get_employe_text("staff_management_btn", lang), reply_markup=staff_management_kb(lang))


@router.message(F.text.func(lambda t: t in btn_texts("ban_management_btn")))
async def open_ban_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="ban_mgmt")
    await message.answer(get_employe_text("ban_management_btn", lang), reply_markup=ban_management_kb(lang))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("market_management_btn")))
async def open_market_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="market_mgmt")
    await message.answer(get_employe_text("market_management_btn", lang), reply_markup=market_management_kb(lang))


@router.message(F.text.func(lambda t: t in btn_texts("product_management_btn")))
async def open_product_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="product_mgmt")
    await message.answer(get_employe_text("product_management_btn", lang), reply_markup=product_management_kb(lang))


@router.message(F.text.func(lambda t: t in btn_texts("statistics_btn")))
async def open_statistics(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_statistic_period)
    await message.answer(
        get_employe_text("statistics_btn", lang) + get_employe_text("statistic_custom_period_hint", lang),
        reply_markup=statistic_period_kb(lang),
    )


@router.message(F.text.func(lambda t: t in btn_texts("back_btn")))
async def go_back(message: Message, state: FSMContext, lang: str):
    data = await state.get_data()
    level = data.get("menu_level", "root")
    is_super_admin = data.get("is_super_admin", False)
    await state.set_state(None)

    if level == "root":
        await state.clear()
        await message.answer("📋", reply_markup=main_menu_kb(lang, is_admin=True))
    else:
        await state.update_data(menu_level="root")
        kb = admin_panel_kb(lang) if is_super_admin else market_admin_panel_kb(lang)
        await message.answer(get_employe_text("admin_panel_welcome", lang), reply_markup=kb)


# ==================== BEKOR QILISH ====================

@router.message(StateFilter(*_ALL_WAITING_STATES), F.text.func(lambda t: t in CANCEL_TEXTS))
async def cancel_admin_action(message: Message, state: FSMContext, lang: str):
    await finish(message, state, lang, get_employe_text("canceled", lang))


@router.callback_query(F.data == "admin_inline_cancel")
async def cancel_inline_selection(callback: CallbackQuery, state: FSMContext, lang: str):
    await finish_cb(callback, state, lang, get_employe_text("canceled", lang))


# ==================== YOZIB QIDIRISH (ro'yxat uzun bo'lganda) ====================

@router.message(
    AdminPanelStates.searching_market,
    F.text,
    F.text.func(lambda t: t not in ALL_ADMIN_BUTTON_TEXTS),
)
async def search_markets(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    prefix = MARKET_SEARCH_PREFIXES.get(data.get("search_context"))
    if not prefix:
        return

    query = message.text.strip().lower()
    all_markets = await get_all_markets(session)
    filtered = [
        m for m in all_markets if query in m.address.lower() or query in m.name.lower()
    ]

    if not filtered:
        await message.answer(get_employe_text("no_results", lang))
        return

    await clear_tracked_list(message.bot, state)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(filtered, prefix, lang),
    )
    await track_list_message(state, sent)


@router.message(
    AdminPanelStates.searching_product,
    F.text,
    F.text.func(lambda t: t not in ALL_ADMIN_BUTTON_TEXTS),
)
async def search_products_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    prefix = PRODUCT_SEARCH_PREFIXES.get(data.get("search_context"))
    market_id = data.get("market_id")
    if not prefix or not market_id:
        return

    query = message.text.strip().lower()
    products = await get_products_by_market(session, market_id)
    filtered = [p for p in products if query in p.name.lower()]

    if not filtered:
        await message.answer(get_employe_text("no_results", lang))
        return

    await clear_tracked_list(message.bot, state)
    sent = await message.answer(
        get_employe_text("choose_product_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=products_select_kb(filtered, prefix, lang),
    )
    await track_list_message(state, sent)


@router.message(
    AdminPanelStates.searching_user,
    F.text,
    F.text.func(lambda t: t not in ALL_ADMIN_BUTTON_TEXTS),
)
async def search_users_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    config = USER_SEARCH_CONFIG.get(data.get("search_context"))
    if not config:
        return

    prompt_key, prefix, list_func = config
    query = message.text.strip().lower()
    users = await list_func(session)
    filtered = [
        u for u in users
        if query in u.full_name.lower()
        or (u.username and query in u.username.lower())
        or query == str(u.telegram_id)
    ]

    if not filtered:
        await message.answer(get_employe_text("no_results", lang))
        return

    await clear_tracked_list(message.bot, state)
    sent = await message.answer(
        get_employe_text(prompt_key, lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(filtered, prefix, lang),
    )
    await track_list_message(state, sent)