from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.category_repo import get_or_create_category
from bot.database.repository.market_repo import (
    create_market,
    delete_market,
    get_all_markets,
    get_market,
    get_market_by_name,
)
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
from bot.database.repository.statistic_repo import get_period_statistics
from bot.database.repository.user_repo import (
    get_user_by_id_or_username,
    list_admins,
    list_banned_users,
    list_staff,
    set_user_banned,
    set_user_role,
)
from bot.enums.enum import UserRole
from bot.filters import IsAdmin, IsSuperAdmin
from bot.keyboards.admin_kb import (
    admin_management_kb,
    admin_panel_kb,
    ban_management_kb,
    cancel_kb,
    confirm_kb,
    market_admin_panel_kb,
    market_choose_kb,
    market_management_kb,
    markets_select_kb,
    product_edit_field_kb,
    product_list_kb,
    product_management_kb,
    products_select_kb,
    staff_management_kb,
    statistic_period_kb,
    users_select_kb,
)
from bot.keyboards.user_kb import main_menu_kb
from bot.lexicons import get_employe_text, get_text
from bot.models import UserModel
from bot.states import AdminPanelStates
from bot.utils.commands import set_commands_for_user
from bot.utils.period import get_preset_period, parse_period

router = Router(name="admin_panel")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

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

_CANCEL_TEXTS = frozenset(get_employe_text("cancel_btn", l) for l in ("uz", "ru", "en"))
_CONFIRM_TEXTS = frozenset(get_employe_text("confirm_btn", l) for l in ("uz", "ru", "en"))

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
_ALL_ADMIN_BUTTON_TEXTS = frozenset(
    get_employe_text(key, l) for key in _ALL_ADMIN_BUTTON_KEYS for l in ("uz", "ru", "en")
)

_MARKET_SEARCH_PREFIXES = {
    "del_market": "del_market_pick",
    "ap_market": "ap_market_pick",
    "dp_market": "dp_market_pick",
    "ep_market": "ep_market_pick",
    "aa_market": "aa_market_pick",
    "as_market": "as_market_pick",
}
_PRODUCT_SEARCH_PREFIXES = {
    "dp_product": "dp_product_pick",
    "ep_product": "ep_product_pick",
}
_USER_SEARCH_CONFIG = {
    "da_user": ("choose_admin_prompt", "da_pick", list_admins),
    "ds_user": ("choose_staff_prompt", "ds_pick", list_staff),
    "un_user": ("choose_banned_prompt", "un_pick", list_banned_users),
}


def _btn_texts(key: str) -> frozenset:
    return frozenset(get_employe_text(key, l) for l in ("uz", "ru", "en"))


def _kb_for_level(level: str, lang: str, is_super_admin: bool = False):
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


async def _finish(message: Message, state: FSMContext, lang: str, text: str) -> None:
    await _clear_tracked_list(message.bot, state)
    data = await state.get_data()
    level = data.get("menu_level", "root")
    is_super_admin = data.get("is_super_admin", False)
    await state.set_state(None)
    await message.answer(text, reply_markup=_kb_for_level(level, lang, is_super_admin))


async def _finish_cb(callback: CallbackQuery, state: FSMContext, lang: str, text: str) -> None:
    await _clear_tracked_list(callback.bot, state)
    data = await state.get_data()
    level = data.get("menu_level", "root")
    is_super_admin = data.get("is_super_admin", False)
    await state.set_state(None)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(text, reply_markup=_kb_for_level(level, lang, is_super_admin))
    await callback.answer()


async def _track_list_message(state: FSMContext, message: Message) -> None:
    """Ro'yxat (tanlash) xabarini FSM data'da eslab qolamiz — keyinroq yozib
    qidirilganda yoki jarayon tugaganda shu eski xabarni o'chirib tashlash uchun."""
    await state.update_data(list_msg_id=message.message_id, list_chat_id=message.chat.id)


async def _clear_tracked_list(bot: Bot, state: FSMContext) -> None:
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

@router.message(F.text.func(lambda t: t in _btn_texts("admin_menu")))
async def show_admin_panel(message: Message, state: FSMContext, lang: str, db_user: UserModel):
    is_super_admin = db_user.role == UserRole.SUPER_ADMIN
    await state.set_state(None)
    await state.update_data(menu_level="root", is_super_admin=is_super_admin)
    kb = admin_panel_kb(lang) if is_super_admin else market_admin_panel_kb(lang)
    await message.answer(get_employe_text("admin_panel_welcome", lang), reply_markup=kb)


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("admin_management_btn")))
async def open_admin_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="admin_mgmt")
    await message.answer(get_employe_text("admin_management_btn", lang), reply_markup=admin_management_kb(lang))


@router.message(F.text.func(lambda t: t in _btn_texts("staff_management_btn")))
async def open_staff_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="staff_mgmt")
    await message.answer(get_employe_text("staff_management_btn", lang), reply_markup=staff_management_kb(lang))


@router.message(F.text.func(lambda t: t in _btn_texts("ban_management_btn")))
async def open_ban_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="ban_mgmt")
    await message.answer(get_employe_text("ban_management_btn", lang), reply_markup=ban_management_kb(lang))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("market_management_btn")))
async def open_market_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="market_mgmt")
    await message.answer(get_employe_text("market_management_btn", lang), reply_markup=market_management_kb(lang))


@router.message(F.text.func(lambda t: t in _btn_texts("product_management_btn")))
async def open_product_management(message: Message, state: FSMContext, lang: str):
    await state.set_state(None)
    await state.update_data(menu_level="product_mgmt")
    await message.answer(get_employe_text("product_management_btn", lang), reply_markup=product_management_kb(lang))


@router.message(F.text.func(lambda t: t in _btn_texts("statistics_btn")))
async def open_statistics(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_statistic_period)
    await message.answer(
        get_employe_text("statistics_btn", lang) + get_employe_text("statistic_custom_period_hint", lang),
        reply_markup=statistic_period_kb(lang),
    )


@router.message(F.text.func(lambda t: t in _btn_texts("back_btn")))
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

@router.message(StateFilter(*_ALL_WAITING_STATES), F.text.func(lambda t: t in _CANCEL_TEXTS))
async def cancel_admin_action(message: Message, state: FSMContext, lang: str):
    await _finish(message, state, lang, get_employe_text("canceled", lang))


@router.callback_query(F.data == "admin_inline_cancel")
async def cancel_inline_selection(callback: CallbackQuery, state: FSMContext, lang: str):
    await _finish_cb(callback, state, lang, get_employe_text("canceled", lang))


# ==================== YOZIB QIDIRISH (ro'yxat uzun bo'lganda) ====================

@router.message(
    AdminPanelStates.searching_market,
    F.text,
    F.text.func(lambda t: t not in _ALL_ADMIN_BUTTON_TEXTS),
)
async def search_markets(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    prefix = _MARKET_SEARCH_PREFIXES.get(data.get("search_context"))
    if not prefix:
        return

    query = message.text.strip().lower()
    all_markets = await get_all_markets(session)
    filtered = [m for m in all_markets if query in m.name.lower()]

    if not filtered:
        await message.answer(get_employe_text("no_results", lang))
        return

    await _clear_tracked_list(message.bot, state)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(filtered, prefix, lang),
    )
    await _track_list_message(state, sent)


@router.message(
    AdminPanelStates.searching_product,
    F.text,
    F.text.func(lambda t: t not in _ALL_ADMIN_BUTTON_TEXTS),
)
async def search_products_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    prefix = _PRODUCT_SEARCH_PREFIXES.get(data.get("search_context"))
    market_id = data.get("market_id")
    if not prefix or not market_id:
        return

    query = message.text.strip().lower()
    products = await get_products_by_market(session, market_id)
    filtered = [p for p in products if query in p.name.lower()]

    if not filtered:
        await message.answer(get_employe_text("no_results", lang))
        return

    await _clear_tracked_list(message.bot, state)
    sent = await message.answer(
        get_employe_text("choose_product_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=products_select_kb(filtered, prefix, lang),
    )
    await _track_list_message(state, sent)


@router.message(
    AdminPanelStates.searching_user,
    F.text,
    F.text.func(lambda t: t not in _ALL_ADMIN_BUTTON_TEXTS),
)
async def search_users_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    config = _USER_SEARCH_CONFIG.get(data.get("search_context"))
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

    await _clear_tracked_list(message.bot, state)
    sent = await message.answer(
        get_employe_text(prompt_key, lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(filtered, prefix, lang),
    )
    await _track_list_message(state, sent)


# ==================== ADMIN BOSHQARUVI ====================

@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("add_admin_btn")))
async def start_add_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="aa_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "aa_market_pick", lang),
    )
    await _track_list_message(state, sent)


@router.callback_query(F.data.startswith("aa_market_pick:"))
async def pick_add_admin_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market_id)
    await state.set_state(AdminPanelStates.waiting_add_admin_id)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        f"<b>{market.address}</b>\n\n" + get_employe_text("add_admin_prompt", lang),
        reply_markup=cancel_kb(lang),
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_add_admin_id, F.text)
async def process_add_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    data = await state.get_data()
    market_id = data.get("market_id")
    if not market_id:
        await _finish(message, state, lang, get_employe_text("market_not_found", lang))
        return

    user = await get_user_by_id_or_username(session, message.text.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return
    await set_user_role(session, user, UserRole.ADMIN, market_id=market_id)
    await set_commands_for_user(bot, user.telegram_id, UserRole.ADMIN, user.language.value)
    await _finish(message, state, lang, get_employe_text("admin_added", lang, name=user.full_name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("delete_admin_btn")))
async def start_delete_admin(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    admins = await list_admins(session)
    if not admins:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="da_user")
    await state.set_state(AdminPanelStates.searching_user)
    sent = await message.answer(
        get_employe_text("choose_admin_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(admins, "da_pick", lang),
    )
    await _track_list_message(state, sent)


@router.callback_query(F.data.startswith("da_pick:"))
async def process_delete_admin(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    user_id = int(callback.data.split(":")[1])
    user = await session.get(UserModel, user_id)
    if not user:
        await callback.answer(get_employe_text("user_not_found", lang), show_alert=True)
        return
    await set_user_role(session, user, UserRole.USER, market_id=None)
    await set_commands_for_user(bot, user.telegram_id, UserRole.USER, user.language.value)
    await _finish_cb(callback, state, lang, get_employe_text("admin_removed", lang, name=user.full_name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("admin_list_btn")))
async def show_admin_list(message: Message, session: AsyncSession, lang: str):
    admins = await list_admins(session)
    if not admins:
        await message.answer(get_employe_text("empty_list", lang))
        return

    lines = []
    for a in admins:
        market = await get_market(session, a.market_id) if a.market_id else None
        market_label = market.address if market else "—"
        name_label = f"{a.full_name} (@{a.username})" if a.username else a.full_name
        lines.append(f"{name_label} — {market_label}")
    await message.answer("\n".join(lines))


# ==================== ISHCHI (STAFF) BOSHQARUVI ====================

@router.message(F.text.func(lambda t: t in _btn_texts("add_staff_btn")))
async def start_add_staff(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    if db_user.role == UserRole.SUPER_ADMIN:
        # Super-admin har doim qaysi do'kon uchun ishchi qo'shayotganini tanlashi kerak
        markets = await get_all_markets(session)
        if not markets:
            await message.answer(get_employe_text("empty_list", lang))
            return
        await state.update_data(search_context="as_market")
        await state.set_state(AdminPanelStates.searching_market)
        sent = await message.answer(
            get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
            reply_markup=markets_select_kb(markets, "as_market_pick", lang),
        )
        await _track_list_message(state, sent)
        return

    # Oddiy (do'konga bog'langan) admin uchun do'kon tanlash shart emas — o'z do'koni ishlatiladi
    await state.update_data(market_id=db_user.market_id)
    await state.set_state(AdminPanelStates.waiting_add_staff_id)
    await message.answer(get_employe_text("add_staff_prompt", lang), reply_markup=cancel_kb(lang))


@router.callback_query(F.data.startswith("as_market_pick:"))
async def pick_add_staff_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market_id)
    await state.set_state(AdminPanelStates.waiting_add_staff_id)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        f"<b>{market.address}</b>\n\n" + get_employe_text("add_staff_prompt", lang),
        reply_markup=cancel_kb(lang),
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_add_staff_id, F.text)
async def process_add_staff(message: Message, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    data = await state.get_data()
    market_id = data.get("market_id")
    if not market_id:
        await _finish(message, state, lang, get_employe_text("market_not_found", lang))
        return

    user = await get_user_by_id_or_username(session, message.text.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return
    await set_user_role(session, user, UserRole.STAFF, market_id=market_id)
    await set_commands_for_user(bot, user.telegram_id, UserRole.STAFF, user.language.value)
    await _finish(message, state, lang, get_employe_text("staff_added", lang, name=user.full_name))


@router.message(F.text.func(lambda t: t in _btn_texts("delete_staff_btn")))
async def start_delete_staff(message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    staff = await list_staff(session, market_id=market_id)
    if not staff:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="ds_user")
    await state.set_state(AdminPanelStates.searching_user)
    sent = await message.answer(
        get_employe_text("choose_staff_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(staff, "ds_pick", lang),
    )
    await _track_list_message(state, sent)


@router.callback_query(F.data.startswith("ds_pick:"))
async def process_delete_staff(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, bot: Bot):
    user_id = int(callback.data.split(":")[1])
    user = await session.get(UserModel, user_id)
    if not user:
        await callback.answer(get_employe_text("user_not_found", lang), show_alert=True)
        return
    await set_user_role(session, user, UserRole.USER, market_id=None)
    await set_commands_for_user(bot, user.telegram_id, UserRole.USER, user.language.value)
    await _finish_cb(callback, state, lang, get_employe_text("staff_removed", lang, name=user.full_name))


@router.message(F.text.func(lambda t: t in _btn_texts("staff_list_btn")))
async def show_staff_list(message: Message, session: AsyncSession, lang: str, db_user: UserModel):
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    staff = await list_staff(session, market_id=market_id)
    if not staff:
        await message.answer(get_employe_text("empty_list", lang))
        return
    lines = [f"{s.full_name} (@{s.username})" if s.username else s.full_name for s in staff]
    await message.answer("\n".join(lines))


# ==================== BAN / UNBAN ====================

@router.message(F.text.func(lambda t: t in _btn_texts("ban_user_btn")))
async def start_ban(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_ban_id)
    await message.answer(get_employe_text("ban_user_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_ban_id, F.text)
async def process_ban(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    user = await get_user_by_id_or_username(session, message.text.strip())
    if not user:
        await message.answer(get_employe_text("user_not_found", lang))
        return
    if user.is_banned:
        await _finish(message, state, lang, get_employe_text("user_already_banned", lang, name=user.full_name))
        return
    await set_user_banned(session, user, True)
    await _finish(message, state, lang, get_employe_text("user_banned", lang, name=user.full_name))


@router.message(F.text.func(lambda t: t in _btn_texts("unban_user_btn")))
async def start_unban(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    banned = await list_banned_users(session)
    if not banned:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="un_user")
    await state.set_state(AdminPanelStates.searching_user)
    sent = await message.answer(
        get_employe_text("choose_banned_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=users_select_kb(banned, "un_pick", lang),
    )
    await _track_list_message(state, sent)


@router.callback_query(F.data.startswith("un_pick:"))
async def process_unban(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    user = await session.get(UserModel, user_id)
    if not user:
        await callback.answer(get_employe_text("user_not_found", lang), show_alert=True)
        return
    await set_user_banned(session, user, False)
    await _finish_cb(callback, state, lang, get_employe_text("user_unbanned", lang, name=user.full_name))


# ==================== DO'KON BOSHQARUVI ====================

@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("add_market_btn")))
async def start_add_market(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_add_market_name)
    await message.answer(get_employe_text("add_market_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_market_name, F.text)
async def process_market_name(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    name = message.text.strip()
    existing = await get_market_by_name(session, name)
    if existing:
        await message.answer(get_employe_text("market_name_exists", lang))
        return
    await state.update_data(market_name=name)
    await state.set_state(AdminPanelStates.waiting_add_market_address)
    await message.answer(get_employe_text("add_market_address_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_market_address, F.text)
async def process_market_address(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    market = await create_market(session, name=data["market_name"], address=message.text.strip())
    await _finish(message, state, lang, get_employe_text("market_added", lang, name=market.name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("delete_market_btn")))
async def start_delete_market(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="del_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "del_market_pick", lang),
    )
    await _track_list_message(state, sent)


@router.callback_query(F.data.startswith("del_market_pick:"))
async def pick_delete_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market.id)
    await state.set_state(AdminPanelStates.waiting_confirm_delete_market)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_employe_text("confirm_delete_market", lang, name=market.name), reply_markup=confirm_kb(lang)
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_confirm_delete_market, F.text.func(lambda t: t in _CONFIRM_TEXTS))
async def process_confirm_delete_market(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    market = await get_market(session, data["market_id"])
    if market:
        await delete_market(session, market)
    await _finish(message, state, lang, get_employe_text("market_deleted", lang, name=market.name if market else ""))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in _btn_texts("market_list_btn")))
async def show_market_list(message: Message, session: AsyncSession, lang: str):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    lines = [f"{m.name} — {m.address}" for m in markets]
    await message.answer("\n".join(lines))


# ==================== MAHSULOT QO'SHISH ====================

@router.message(F.text.func(lambda t: t in _btn_texts("add_product_btn")))
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
    await _track_list_message(state, sent)


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
async def process_add_product_price(message: Message, state: FSMContext, lang: str):
    try:
        price = float(message.text.strip())
    except ValueError:
        await message.answer(get_employe_text("only_numbers", lang))
        return
    await state.update_data(price=price)
    await state.set_state(AdminPanelStates.waiting_add_product_category)
    await message.answer(get_employe_text("add_product_category_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_product_category, F.text)
async def process_add_product_category(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    category_name = "Umumiy" if message.text.strip() == "-" else message.text.strip()
    category = await get_or_create_category(session, category_name)
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
    )

    if created:
        text = get_employe_text("product_added", lang, name=product.name, price=f"{product.price:,.0f}")
    else:
        text = get_employe_text(
            "product_restocked", lang, name=product.name, stock=data["quantity"], total=product.stock
        )

    await _finish(message, state, lang, text)


@router.message(AdminPanelStates.waiting_add_product_photo, F.photo)
async def process_add_product_photo(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    file_id = message.photo[-1].file_id
    await _create_product_and_finish(message, session, lang, state, file_id)


@router.message(AdminPanelStates.waiting_add_product_photo, F.text == "-")
async def skip_add_product_photo(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    await _create_product_and_finish(message, session, lang, state, None)


# ==================== MAHSULOT O'CHIRISH ====================

@router.message(F.text.func(lambda t: t in _btn_texts("delete_product_btn")))
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
        await _track_list_message(state, sent)
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
    await _track_list_message(state, sent)


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


@router.message(AdminPanelStates.waiting_confirm_delete_product, F.text.func(lambda t: t in _CONFIRM_TEXTS))
async def process_confirm_delete_product(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if product:
        await delete_product(session, product)
    await _finish(
        message, state, lang, get_employe_text("product_deleted", lang, name=product.name if product else "")
    )


# ==================== MAHSULOTNI TAHRIRLASH (nomi, tavsifi, narxi, miqdori, kategoriyasi, rasmi) ====================

@router.message(F.text.func(lambda t: t in _btn_texts("edit_product_price_btn")))
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
        await _track_list_message(state, sent)
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
    await _track_list_message(state, sent)


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
        await _finish(message, state, lang, get_employe_text("product_not_found", lang))
        return
    new_name = message.text.strip()
    await update_product_name(session, product, new_name)
    await _finish(message, state, lang, get_employe_text("product_name_updated", lang, name=new_name))


@router.message(AdminPanelStates.waiting_edit_description_value, F.text)
async def process_edit_description(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await _finish(message, state, lang, get_employe_text("product_not_found", lang))
        return
    await update_product_description(session, product, message.text.strip())
    await _finish(message, state, lang, get_employe_text("product_description_updated", lang))


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
        await _finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    await update_product_price(session, product, new_price)
    await _finish(
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
        await _finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    new_stock = max(0, int(message.text.strip()))
    await update_product_stock(session, product, new_stock)
    await _finish(message, state, lang, get_employe_text("product_stock_updated", lang, stock=new_stock))


@router.message(AdminPanelStates.waiting_edit_category_value, F.text)
async def process_edit_category(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await _finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    category_name = message.text.strip()
    category = await get_or_create_category(session, category_name)
    await update_product_category(session, product, category.id)
    await _finish(message, state, lang, get_employe_text("product_category_updated", lang, name=category_name))


@router.message(AdminPanelStates.waiting_edit_photo_value, F.photo)
async def process_edit_photo(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    product = await get_product(session, data["product_id"])
    if not product:
        await _finish(message, state, lang, get_employe_text("product_not_found", lang))
        return

    file_id = message.photo[-1].file_id
    await update_product_photo(session, product, file_id)
    await _finish(message, state, lang, get_employe_text("product_photo_updated", lang))


# ==================== MAHSULOTLAR RO'YXATI (do'kon tanlash orqali) ====================

@router.message(F.text.func(lambda t: t in _btn_texts("product_list_btn")))
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


# ==================== STATISTIKA (tayyor davrlar) ====================

@router.callback_query(F.data.startswith("statistic:"))
async def show_preset_statistics(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel):
    preset = callback.data.split(":")[1]
    start, end = get_preset_period(preset)
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    stats = await get_period_statistics(session, start, end, market_id=market_id)
    period_label = get_employe_text(f"statistic_period_{preset}", lang)

    await state.set_state(None)
    await callback.message.edit_text(
        get_employe_text("statistic_title", lang, period=period_label)
        + "\n\n"
        + get_employe_text(
            "statistic_body",
            lang,
            markets_count=stats["markets_count"],
            staff_count=stats["staff_count"],
            sold_qty=stats["sold_qty"],
            delivered_qty=stats["delivered_qty"],
            pickup_qty=stats["pickup_qty"],
            sold_sum=f"{stats['sold_sum']:,.0f}",
            stock_qty=stats["stock_qty"],
            stock_sum=f"{stats['stock_sum']:,.0f}",
        )
    )
    await callback.answer()


@router.message(
    AdminPanelStates.waiting_statistic_period,
    F.text,
    F.text.func(lambda t: t not in _ALL_ADMIN_BUTTON_TEXTS),
)
async def process_custom_statistic_period(
    message: Message, session: AsyncSession, lang: str, state: FSMContext, db_user: UserModel
):
    parsed = parse_period(message.text.strip())
    if not parsed:
        await message.answer(get_employe_text("invalid_period", lang))
        return

    start, end, label = parsed
    market_id = None if db_user.role == UserRole.SUPER_ADMIN else db_user.market_id
    stats = await get_period_statistics(session, start, end, market_id=market_id)

    text = (
        get_employe_text("statistic_title", lang, period=label)
        + "\n\n"
        + get_employe_text(
            "statistic_body",
            lang,
            markets_count=stats["markets_count"],
            staff_count=stats["staff_count"],
            sold_qty=stats["sold_qty"],
            delivered_qty=stats["delivered_qty"],
            pickup_qty=stats["pickup_qty"],
            sold_sum=f"{stats['sold_sum']:,.0f}",
            stock_qty=stats["stock_qty"],
            stock_sum=f"{stats['stock_sum']:,.0f}",
        )
    )
    await _finish(message, state, lang, text)
