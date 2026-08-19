from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.lexicons import get_text
from bot.lexicons.lexicon_employe import get_employe_text
from bot.models import CategoryModel, MarketModel, ProductsModel


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def phone_request_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text("share_phone_btn", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def location_request_kb(lang: str) -> ReplyKeyboardMarkup:
    """
    Manzilni xaritadan yuborish tugmasi. Diqqat: foydalanuvchi shu klaviatura
    ko'rinib turgan holatda ham oddiy matn yozishi mumkin — ikkalasi ham
    ishlaydi (tugma orqali koordinata, matn orqali qo'lda yozilgan manzil).
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text("send_location_btn", lang), request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def address_input_kb(lang: str) -> ReplyKeyboardMarkup:
    """location_request_kb bilan bir xil, lekin "Orqaga" tugmasi ham bor —
    manzil o'zgartirish bosqichida foydalanuvchi bekor qilib qaytishi uchun."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text("send_location_btn", lang), request_location=True)],
            [KeyboardButton(text=get_text("back_btn", lang))],
        ],
        resize_keyboard=True,
    )


def main_menu_kb(lang: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    if is_admin:
        # Admin uchun xaridor funksiyalari (xarid, savat, profil, sozlamalar)
        # asosiy menyuda ko'rsatilmaydi — ular endi Admin panel ichidagi
        # "⚙️ Sozlamalar" bo'limi orqali kiriladi.
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=get_employe_text("admin_menu", lang))]],
            resize_keyboard=True,
        )

    keyboard = [
        [KeyboardButton(text=get_text("menu_shopping", lang))],
        [
            KeyboardButton(text=get_text("menu_cart", lang)),
            KeyboardButton(text=get_text("menu_profile", lang)),
        ],
        [KeyboardButton(text=get_text("menu_settings", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def markets_kb(markets: list[MarketModel]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=m.address, callback_data=f"market:{m.id}")] for m in markets
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def categories_kb(categories: list[CategoryModel], market_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=c.name, callback_data=f"cat:{market_id}:{c.id}")]
        for c in categories
    ]
    buttons.append(
        [InlineKeyboardButton(text="⬅️", callback_data="back_to_markets")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_kb(products: list[ProductsModel], market_id: int, category_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{p.name} — {p.price:,.0f}",
                callback_data=f"product:{market_id}:{category_id}:{p.id}",
            )
        ]
        for p in products
    ]
    buttons.append(
        [InlineKeyboardButton(text="⬅️", callback_data=f"back_to_categories:{market_id}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_detail_kb(
    product_id: int, quantity: int, lang: str, market_id: int, category_id: int
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("add_to_cart_btn", lang),
                    callback_data=f"cart_add:{market_id}:{category_id}:{product_id}:{quantity}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="<<", callback_data=f"qty_dec:{market_id}:{category_id}:{product_id}:{quantity}"
                ),
                InlineKeyboardButton(text=str(quantity), callback_data="noop"),
                InlineKeyboardButton(
                    text=">>", callback_data=f"qty_inc:{market_id}:{category_id}:{product_id}:{quantity}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text("back_btn", lang),
                    callback_data=f"back_to_products:{market_id}:{category_id}",
                )
            ],
        ]
    )


def cart_kb(cart_items: list[dict], lang: str) -> InlineKeyboardMarkup:
    buttons = []
    for item in cart_items:
        pid = item["product_id"]
        buttons.append(
            [
                InlineKeyboardButton(text="➖", callback_data=f"cart_dec:{pid}"),
                InlineKeyboardButton(
                    text=f"{item['name']} x{item['quantity']}", callback_data="noop"
                ),
                InlineKeyboardButton(text="➕", callback_data=f"cart_inc:{pid}"),
                InlineKeyboardButton(text="❌", callback_data=f"cart_del:{pid}"),
            ]
        )
    if cart_items:
        buttons.append(
            [InlineKeyboardButton(text=get_text("cart_order_btn", lang), callback_data="checkout")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def delivery_type_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("pickup_btn", lang), callback_data="delivery:pickup")],
            [InlineKeyboardButton(text=get_text("delivery_btn", lang), callback_data="delivery:delivery")],
        ]
    )


def confirm_order_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("order_confirm_btn", lang), callback_data="order_confirm"),
                InlineKeyboardButton(text=get_text("order_cancel_btn", lang), callback_data="order_cancel"),
            ]
        ]
    )


def settings_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("settings_language_btn", lang), callback_data="settings:lang")],
            [InlineKeyboardButton(text=get_text("settings_address_btn", lang), callback_data="settings:address")],
            [InlineKeyboardButton(text=get_text("settings_name_btn", lang), callback_data="settings:name")],
        ]
    )
