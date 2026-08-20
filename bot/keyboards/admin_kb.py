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
    """SUPER_ADMIN uchun to'liq panel — barcha do'konlarni boshqarish imkoniyati bilan."""
    keyboard = [
        [
            KeyboardButton(text=get_employe_text("admin_management_btn", lang)),
            KeyboardButton(text=get_employe_text("staff_management_btn", lang)),
        ],
        [
            KeyboardButton(text=get_employe_text("ban_management_btn", lang)),
            KeyboardButton(text=get_employe_text("market_management_btn", lang)),
        ],
        [
            KeyboardButton(text=get_employe_text("product_management_btn", lang)),
            KeyboardButton(text=get_employe_text("statistics_btn", lang)),
        ],
        [KeyboardButton(text=get_text("menu_settings", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def market_admin_panel_kb(lang: str) -> ReplyKeyboardMarkup:
    """Oddiy (bitta do'konga tegishli) ADMIN uchun qisqartirilgan panel —
    faqat o'z do'koniga tegishli bo'limlar: ishchilar, mahsulotlar, statistika.
    Admin/Do'kon boshqaruvi (butun platformaga tegishli) ko'rinmaydi."""
    keyboard = [
        [
            KeyboardButton(text=get_employe_text("staff_management_btn", lang)),
            KeyboardButton(text=get_employe_text("product_management_btn", lang)),
        ],
        [
            KeyboardButton(text=get_employe_text("ban_management_btn", lang)),
            KeyboardButton(text=get_employe_text("statistics_btn", lang)),
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
