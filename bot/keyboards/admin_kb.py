from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.lexicons.lexicon_employe import LEXICON_COMMANDS_ADMIN, get_employe_text
from bot.lexicons.lexicon_text import get_text
from bot.models import OrderModel


def accept_order_kb(order: OrderModel, lang: str) -> InlineKeyboardMarkup:
    """Buyurtmani qabul qilish uchun inline tugma (eski, oddiy variant)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_employe_text("accept_order_btn", lang),
                    callback_data=f"staff_accept:{order.id}",
                )
            ]
        ]
    )


def admin_panel_commands_kb(lang: str) -> InlineKeyboardMarkup:
    """
    Admin uchun barcha komandalarni tugma ko'rinishida ko'rsatadi
    (LEXICON_COMMANDS_ADMIN asosida — bitta joyda saqlanadi, takrorlanmaydi).
    /start va /help argument talab qilmagani uchun ro'yxatga kiritilmaydi.
    """
    pairs = LEXICON_COMMANDS_ADMIN.get(lang, LEXICON_COMMANDS_ADMIN["uz"])
    buttons = [
        [InlineKeyboardButton(text=f"/{cmd} — {desc}", callback_data=f"admin_cmd_info:{cmd}")]
        for cmd, desc in pairs
        if cmd not in ("start", "help")
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== REPLY KEYBOARD TUGMALAR ====================

def admin_panel_kb(lang: str) -> ReplyKeyboardMarkup:
    """SUPER_ADMIN uchun to'liq panel — barcha do'konlarni boshqarish imkoniyati bilan.
    Mahsulot/Kategoriya/Brend boshqaruvi bitta 'Mahsulotlar bo'limi' submenyusiga
    yig'ilgan — asosiy panelda tugmalar kamroq bo'lishi uchun."""
    keyboard = [
        [
            KeyboardButton(text=get_employe_text("admin_management_btn", lang)),
            # STAFF boshqaruvi vaqtincha uzib qo'yilgan — qayta yoqish bot/handlers/admin/__init__.py'da
            KeyboardButton(text=get_employe_text("market_management_btn", lang)),
        ],
        [
            KeyboardButton(text=get_employe_text("ban_management_btn", lang)),
            KeyboardButton(text=get_employe_text("catalog_management_btn", lang)),
        ],
        [
            KeyboardButton(text=get_employe_text("statistics_btn", lang)),
            KeyboardButton(text=get_employe_text("feedback_management_btn", lang)),
        ],
        [
            KeyboardButton(text=get_employe_text("orders_list_btn", lang)),
            KeyboardButton(text=get_text("menu_settings", lang))
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def catalog_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """'Mahsulotlar bo'limi' submenyusi — Mahsulot/Kategoriya/Brend boshqaruvi
    shu yerga yig'ilgan (faqat SUPER_ADMIN uchun)."""
    keyboard = [
        [KeyboardButton(text=get_employe_text("product_management_btn", lang))],
        [
            KeyboardButton(text=get_employe_text("category_management_btn", lang)),
            KeyboardButton(text=get_employe_text("brand_management_btn", lang)),
        ],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def market_admin_panel_kb(lang: str) -> ReplyKeyboardMarkup:
    """Oddiy (bitta do'konga tegishli) ADMIN uchun qisqartirilgan panel —
    platforma darajasidagi bo'limlar (Admin/Do'kon/Kategoriya/Brend) faqat
    SUPER_ADMIN'da ko'rinadi. STAFF boshqaruvi vaqtincha uzib qo'yilgan."""
    keyboard = [
        [
            # STAFF boshqaruvi vaqtincha uzib qo'yilgan — qarang: bot/handlers/admin/__init__.py
            KeyboardButton(text=get_employe_text("product_management_btn", lang)),
        ],
        [
            KeyboardButton(text=get_employe_text("ban_management_btn", lang)),
            KeyboardButton(text=get_employe_text("statistics_btn", lang)),
        ],
        [KeyboardButton(text=get_employe_text("feedback_management_btn", lang)),
        KeyboardButton(text=get_employe_text("orders_list_btn", lang)),
        ],
        [KeyboardButton(text=get_text("menu_settings", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def admin_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """Admin boshqaruvi tugmalari"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("add_admin_btn", lang))],
        [KeyboardButton(text=get_employe_text("delete_admin_btn", lang))],
        [KeyboardButton(text=get_employe_text("admin_list_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def staff_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """Staff boshqaruvi tugmalari"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("add_staff_btn", lang))],
        [KeyboardButton(text=get_employe_text("delete_staff_btn", lang))],
        [KeyboardButton(text=get_employe_text("staff_list_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def ban_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """Ban boshqaruvi tugmalari"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("ban_user_btn", lang))],
        [KeyboardButton(text=get_employe_text("unban_user_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def market_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """Do'kon boshqaruvi tugmalari"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("add_market_btn", lang))],
        [KeyboardButton(text=get_employe_text("delete_market_btn", lang))],
        [KeyboardButton(text=get_employe_text("market_list_btn", lang))],
        [KeyboardButton(text=get_employe_text("link_billz_btn", lang))],
        [KeyboardButton(text=get_employe_text("sync_billz_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def product_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """Mahsulot boshqaruvi tugmalari"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("add_product_btn", lang))],
        [KeyboardButton(text=get_employe_text("delete_product_btn", lang))],
        [KeyboardButton(text=get_employe_text("product_list_btn", lang))],
        [KeyboardButton(text=get_employe_text("edit_product_price_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def category_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """Kategoriya boshqaruvi tugmalari"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("add_category_btn", lang))],
        [KeyboardButton(text=get_employe_text("delete_category_btn", lang))],
        [KeyboardButton(text=get_employe_text("category_list_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def brand_management_kb(lang: str) -> ReplyKeyboardMarkup:
    """Brend boshqaruvi tugmalari"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("add_brand_btn", lang))],
        [KeyboardButton(text=get_employe_text("delete_brand_btn", lang))],
        [KeyboardButton(text=get_employe_text("brand_list_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ==================== QO'SHIMCHA TUGMALAR ====================

def back_kb(lang: str) -> ReplyKeyboardMarkup:
    """Faqat Orqaga tugmasi"""
    keyboard = [[KeyboardButton(text=get_employe_text("back_btn", lang))]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def confirm_kb(lang: str) -> ReplyKeyboardMarkup:
    """Tasdiqlash uchun tugmalar"""
    keyboard = [
        [
            KeyboardButton(text=get_employe_text("confirm_btn", lang)),
            KeyboardButton(text=get_employe_text("cancel_btn", lang)),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi"""
    keyboard = [[KeyboardButton(text=get_employe_text("cancel_btn", lang))]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ==================== STAFF TUGMALAR ====================

def staff_panel_kb(lang: str) -> ReplyKeyboardMarkup:
    """Staff panel uchun asosiy tugmalar"""
    keyboard = [
        [KeyboardButton(text=get_employe_text("statistics_btn", lang))],
        [KeyboardButton(text=get_employe_text("back_btn", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ==================== INLINE TUGMALAR ====================

def order_action_kb(order_id: int, lang: str) -> InlineKeyboardMarkup:
    """Buyurtma uchun qabul qilish / rad etish tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_employe_text("accept_order_btn", lang),
                    callback_data=f"staff_accept:{order_id}",
                ),
                InlineKeyboardButton(
                    text=get_employe_text("reject_order_btn", lang),
                    callback_data=f"staff_reject:{order_id}",
                ),
            ],
        ]
    )


def statistic_period_kb(lang: str) -> InlineKeyboardMarkup:
    """Statistika uchun davr tanlash tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_employe_text("statistic_period_today", lang),
                    callback_data="statistic:today",
                ),
                InlineKeyboardButton(
                    text=get_employe_text("statistic_period_week", lang),
                    callback_data="statistic:week",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_employe_text("statistic_period_month", lang),
                    callback_data="statistic:month",
                ),
                InlineKeyboardButton(
                    text=get_employe_text("statistic_period_year", lang),
                    callback_data="statistic:year",
                ),
            ],
        ]
    )


def product_edit_field_kb(product_id: int, lang: str) -> InlineKeyboardMarkup:
    """Mahsulotning qaysi maydonini tahrirlash kerakligini tanlash uchun tugmalar."""
    fields = [
        ("name", "edit_field_name_btn"),
        ("description", "edit_field_description_btn"),
        ("price", "edit_field_price_btn"),
        ("stock", "edit_field_stock_btn"),
        ("category", "edit_field_category_btn"),
        ("photo", "edit_field_photo_btn"),
    ]
    buttons = [
        [InlineKeyboardButton(text=get_employe_text(label_key, lang), callback_data=f"edit_field:{field}:{product_id}")]
        for field, label_key in fields
    ]
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def market_choose_kb(markets: list, lang: str) -> InlineKeyboardMarkup:
    """Do'kon tanlash uchun inline tugmalar"""
    buttons = []
    for market in markets:
        buttons.append(
            [InlineKeyboardButton(text=market.address, callback_data=f"market_choose:{market.id}")]
        )
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("back_btn", lang), callback_data="back_to_admin")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_list_kb(products: list, lang: str) -> InlineKeyboardMarkup:
    """Mahsulotlar ro'yxati uchun inline tugmalar"""
    buttons = []
    for product in products:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{product.name} - {product.price} so'm",
                    callback_data=f"product_info:{product.id}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("back_btn", lang), callback_data="back_to_admin")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== TANLASH (SELECT) TUGMALARI — matn kiritish o'rniga ====================

def has_billz_kb(market_id: int, lang: str) -> InlineKeyboardMarkup:
    """Yangi do'kon qo'shilgandan keyin — 'Bu do'konda Billz tizimi bormi?'
    savoliga javob tugmalari."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_employe_text("yes_btn", lang), callback_data=f"new_market_billz:yes:{market_id}"),
                InlineKeyboardButton(text=get_employe_text("no_btn", lang), callback_data=f"new_market_billz:no:{market_id}"),
            ]
        ]
    )


def markets_select_kb(markets: list, callback_prefix: str, lang: str) -> InlineKeyboardMarkup:
    """Do'konlar ro'yxatidan bittasini tanlash (o'chirish, mahsulot qo'shish va h.k. uchun)."""
    buttons = [
        [InlineKeyboardButton(text=m.address, callback_data=f"{callback_prefix}:{m.id}")] for m in markets
    ]
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_select_kb(products: list, callback_prefix: str, lang: str) -> InlineKeyboardMarkup:
    """Mahsulotlar ro'yxatidan bittasini tanlash (o'chirish, narx tahrirlash uchun)."""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{p.name} — {p.price:,.0f}", callback_data=f"{callback_prefix}:{p.id}"
            )
        ]
        for p in products
    ]
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def users_select_kb(users: list, callback_prefix: str, lang: str) -> InlineKeyboardMarkup:
    """Foydalanuvchilar ro'yxatidan bittasini tanlash (admin/staff o'chirish, unban uchun)."""
    buttons = []
    for u in users:
        label = f"{u.full_name} (@{u.username})" if u.username else u.full_name
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"{callback_prefix}:{u.id}")])
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def categories_select_kb(categories: list, callback_prefix: str, lang: str) -> InlineKeyboardMarkup:
    """Kategoriyalar ro'yxatidan bittasini tanlash (o'chirish uchun)."""
    buttons = [
        [InlineKeyboardButton(text=c.name, callback_data=f"{callback_prefix}:{c.id}")] for c in categories
    ]
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def categories_pick_kb(categories: list, callback_prefix: str, lang: str) -> InlineKeyboardMarkup:
    """Mahsulot qo'shish jarayonida kategoriya tanlash — ro'yxatda yo'q bo'lsa
    o'sha yerning o'zida yangisini qo'shish imkoniyati bilan."""
    buttons = [
        [InlineKeyboardButton(text=c.name, callback_data=f"{callback_prefix}:{c.id}")] for c in categories
    ]
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("add_new_category_btn", lang), callback_data=f"{callback_prefix}:new")]
    )
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def brands_select_kb(brands: list, callback_prefix: str, lang: str) -> InlineKeyboardMarkup:
    """Brendlar ro'yxatidan bittasini tanlash (o'chirish uchun)."""
    buttons = [
        [InlineKeyboardButton(text=b.name, callback_data=f"{callback_prefix}:{b.id}")] for b in brands
    ]
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def brands_pick_kb(brands: list, callback_prefix: str, lang: str) -> InlineKeyboardMarkup:
    """Mahsulot qo'shish jarayonida brend tanlash — 'brendsiz' va yangi brend
    qo'shish imkoniyatlari bilan."""
    buttons = [
        [InlineKeyboardButton(text=b.name, callback_data=f"{callback_prefix}:{b.id}")] for b in brands
    ]
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("no_brand_btn", lang), callback_data=f"{callback_prefix}:none")]
    )
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("add_new_brand_btn", lang), callback_data=f"{callback_prefix}:new")]
    )
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("cancel_btn", lang), callback_data="admin_inline_cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def feedback_nav_kb(offset: int, total: int, is_reviewed: bool, feedback_id: int, lang: str) -> InlineKeyboardMarkup:
    """Fikr-mulohazalarni birma-bir ko'rish uchun navigatsiya (◀️/▶️),
    'ko'rib chiqildi' belgisi va yopish tugmasi."""
    nav_row = []
    if offset > 0:
        nav_row.append(
            InlineKeyboardButton(text="◀️", callback_data=f"fb_nav:{offset - 1}")
        )
    if offset < total - 1:
        nav_row.append(
            InlineKeyboardButton(text="▶️", callback_data=f"fb_nav:{offset + 1}")
        )

    buttons = []
    if nav_row:
        buttons.append(nav_row)
    if not is_reviewed:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=get_employe_text("mark_reviewed_btn", lang),
                    callback_data=f"fb_mark:{feedback_id}:{offset}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("close_btn", lang), callback_data="fb_close")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== BUYURTMALAR RO'YXATI (holat bo'yicha, sahifalab) ====================

def orders_status_kb(lang: str) -> InlineKeyboardMarkup:
    """'📦 Buyurtmalar' bosilganda chiqadigan holat-filtr tugmalari."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_employe_text("order_status_new", lang), callback_data="ord_status:new")],
            [InlineKeyboardButton(text=get_employe_text("order_status_confirmed", lang), callback_data="ord_status:confirmed")],
            [InlineKeyboardButton(text=get_employe_text("order_status_canceled", lang), callback_data="ord_status:canceled")],
        ]
    )


def orders_page_kb(orders: list, status_key: str, page: int, total_pages: int, lang: str) -> InlineKeyboardMarkup:
    """Bitta holatdagi buyurtmalar ro'yxati — har biri alohida qatorda
    (buyurtma raqami + mijoz + summa), pastda sahifalash (◀️ 1/2 ▶️)."""
    buttons = []
    for order in orders:
        customer = order.user.full_name if order.user else "-"
        label = f"#{order.id} — {customer} — {order.total_price:,.0f}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"ord_view:{order.id}:{status_key}:{page}")])

    if total_pages > 1:
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton(text="◀️", callback_data=f"ord_page:{status_key}:{page - 1}"))
        nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop_page"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(text="▶️", callback_data=f"ord_page:{status_key}:{page + 1}"))
        buttons.append(nav_row)

    buttons.append(
        [InlineKeyboardButton(text=get_employe_text("close_btn", lang), callback_data="fb_close")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def order_detail_back_kb(status_key: str, page: int, lang: str) -> InlineKeyboardMarkup:
    """Buyurtma tafsilotidan ro'yxatga qaytish tugmasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_employe_text("back_btn", lang), callback_data=f"ord_page:{status_key}:{page}")]
        ]
    )


def order_detail_action_kb(order_id: int, status_key: str, page: int, lang: str) -> InlineKeyboardMarkup:
    """Buyurtma tafsiloti uchun — YANGI (NEW) holatdagi buyurtmalarda
    Qabul qilish/Rad etish tugmalari, pastda ro'yxatga qaytish."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_employe_text("accept_order_btn", lang), callback_data=f"staff_accept:{order_id}"),
                InlineKeyboardButton(text=get_employe_text("reject_order_btn", lang), callback_data=f"staff_reject:{order_id}"),
            ],
            [InlineKeyboardButton(text=get_employe_text("back_btn", lang), callback_data=f"ord_page:{status_key}:{page}")],
        ]
    )
