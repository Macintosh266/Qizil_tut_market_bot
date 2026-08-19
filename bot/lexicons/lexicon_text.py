"""
Oddiy dictionary-asosidagi i18n. Har bir kalit uchun uz/ru/en tarjimasi bor.
Katta loyihalar uchun fluent/gettext tavsiya etiladi, lekin bu loyiha
hajmi uchun bu yondashuv yetarli va tushunarli.
"""

LEXICON_TEXT: dict[str, dict[str, str]] = {
    "choose_language": {
        "uz": "Tilni tanlang:",
        "ru": "Выберите язык:",
        "en": "Choose your language:",
    },
    "welcome": {
        "uz": "Assalomu alaykum, {name}! 🛍 Online do'konimizga xush kelibsiz.",
        "ru": "Здравствуйте, {name}! 🛍 Добро пожаловать в наш онлайн-магазин.",
        "en": "Hello, {name}! 🛍 Welcome to our online market.",
    },
    "share_phone": {
        "uz": "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring:",
        "ru": "Отправьте номер телефона для регистрации:",
        "en": "Please share your phone number to register:",
    },
    "share_phone_btn": {
        "uz": "📱 Raqamni yuborish",
        "ru": "📱 Отправить номер",
        "en": "📱 Share phone number",
    },
    "menu_shopping": {"uz": "🛍 Xarid qilish", "ru": "🛍 Покупки", "en": "🛍 Shopping"},
    "menu_cart": {"uz": "🛒 Savat", "ru": "🛒 Корзина", "en": "🛒 Cart"},
    "menu_profile": {"uz": "👤 Profil", "ru": "👤 Профиль", "en": "👤 Profile"},
    "menu_settings": {"uz": "⚙️ Sozlamalar", "ru": "⚙️ Настройки", "en": "⚙️ Settings"},
    "choose_market": {
        "uz": "Do'konni tanlang:",
        "ru": "Выберите магазин:",
        "en": "Choose a market:",
    },
    "no_markets": {
        "uz": "Hozircha do'konlar mavjud emas.",
        "ru": "Пока нет доступных магазинов.",
        "en": "No markets available yet.",
    },
    "choose_category": {
        "uz": "Kategoriyani tanlang:",
        "ru": "Выберите категорию:",
        "en": "Choose a category:",
    },
    "no_categories": {
        "uz": "Bu do'konda kategoriyalar yo'q.",
        "ru": "В этом магазине нет категорий.",
        "en": "This market has no categories.",
    },
    "no_products": {
        "uz": "Bu kategoriyada mahsulotlar yo'q.",
        "ru": "В этой категории нет товаров.",
        "en": "No products in this category.",
    },
    "search_hint": {
        "uz": "🔍 Mahsulot qidirish uchun uning nomini yozing.",
        "ru": "🔍 Введите название товара для поиска.",
        "en": "🔍 Type a product name to search.",
    },
    "product_price": {"uz": "💰 Narxi", "ru": "💰 Цена", "en": "💰 Price"},
    "product_stock": {"uz": "📦 Omborda", "ru": "📦 В наличии", "en": "📦 In stock"},
    "add_to_cart_btn": {
        "uz": "🛒 Savatga qo'shish",
        "ru": "🛒 В корзину",
        "en": "🛒 Add to cart",
    },
    "back_btn": {
        "uz": "⬅️ Orqaga qaytish",
        "ru": "⬅️ Назад",
        "en": "⬅️ Go back",
    },
    "enter_quantity": {
        "uz": "Nechta dona olmoqchisiz? (son kiriting)",
        "ru": "Сколько штук хотите? (введите число)",
        "en": "How many would you like? (enter a number)",
    },
    "invalid_number": {
        "uz": "Noto'g'ri son. Qaytadan urinib ko'ring.",
        "ru": "Неверное число. Попробуйте снова.",
        "en": "Invalid number. Please try again.",
    },
    "not_enough_stock": {
        "uz": "Omborda faqat {stock} dona qoldi.",
        "ru": "В наличии осталось только {stock} шт.",
        "en": "Only {stock} left in stock.",
    },
    "added_to_cart": {
        "uz": "✅ Savatga qo'shildi!",
        "ru": "✅ Добавлено в корзину!",
        "en": "✅ Added to cart!",
    },
    "cart_empty": {
        "uz": "Savatingiz bo'sh.",
        "ru": "Ваша корзина пуста.",
        "en": "Your cart is empty.",
    },
    "cart_title": {
        "uz": "🛒 Sizning savatingiz:",
        "ru": "🛒 Ваша корзина:",
        "en": "🛒 Your cart:",
    },
    "cart_total": {"uz": "💰 Jami", "ru": "💰 Итого", "en": "💰 Total"},
    "cart_edit_btn": {
        "uz": "✏️ O'zgartirish",
        "ru": "✏️ Изменить",
        "en": "✏️ Edit",
    },
    "cart_order_btn": {
        "uz": "✅ Buyurtma qilish",
        "ru": "✅ Оформить заказ",
        "en": "✅ Place order",
    },
    "choose_delivery_type": {
        "uz": "Buyurtmani qanday olmoqchisiz?",
        "ru": "Как вы хотите получить заказ?",
        "en": "How would you like to receive your order?",
    },
    "pickup_btn": {
        "uz": "🚶 O'zim olib ketaman",
        "ru": "🚶 Заберу сам",
        "en": "🚶 I'll pick it up",
    },
    "delivery_btn": {
        "uz": "🚚 Yetkazib berish",
        "ru": "🚚 Доставка",
        "en": "🚚 Delivery",
    },
    "enter_address": {
        "uz": "Yetkazib berish manzilini yozing, yoki quyidagi tugma orqali xaritadan joylashuvingizni yuboring:",
        "ru": "Введите адрес доставки, или отправьте геолокацию через кнопку ниже:",
        "en": "Type your delivery address, or send your location using the button below:",
    },
    "send_location_btn": {
        "uz": "📍 Joylashuvni yuborish (xaritadan)",
        "ru": "📍 Отправить геолокацию (с карты)",
        "en": "📍 Send location (from map)",
    },
    "location_saved_address": {
        "uz": "📍 Xaritadan belgilangan joylashuv",
        "ru": "📍 Местоположение с карты",
        "en": "📍 Location pinned on map",
    },
    "order_confirm": {
        "uz": "📋 Buyurtmani tasdiqlang:",
        "ru": "📋 Подтвердите заказ:",
        "en": "📋 Confirm your order:",
    },
    "order_confirm_btn": {
        "uz": "✅ Tasdiqlash",
        "ru": "✅ Подтвердить",
        "en": "✅ Confirm",
    },
    "order_cancel_btn": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Отменить",
        "en": "❌ Cancel",
    },
    "order_placed": {
        "uz": "✅ Buyurtmangiz qabul qilindi! Raqami: #{order_id}",
        "ru": "✅ Ваш заказ принят! Номер: #{order_id}",
        "en": "✅ Your order has been placed! Order #{order_id}",
    },
    "order_canceled": {
        "uz": "❌ Buyurtma bekor qilindi.",
        "ru": "❌ Заказ отменён.",
        "en": "❌ Order canceled.",
    },
    "canceled": {
        "uz": "❌ Bekor qilindi.",
        "ru": "❌ Отменено.",
        "en": "❌ Canceled.",
    },
    "profile_info": {
        "uz": (
            "👤 Profil\n\nID: {id}\nIsm: {name}\nUsername: {username}\n"
            "Til: {language}\nTelefon: {phone}\nManzil: {address}"
        ),
        "ru": (
            "👤 Профиль\n\nID: {id}\nИмя: {name}\nUsername: {username}\n"
            "Язык: {language}\nТелефон: {phone}\nАдрес: {address}"
        ),
        "en": (
            "👤 Profile\n\nID: {id}\nName: {name}\nUsername: {username}\n"
            "Language: {language}\nPhone: {phone}\nAddress: {address}"
        ),
    },
    "settings_menu": {
        "uz": "Nimani o'zgartirmoqchisiz?",
        "ru": "Что хотите изменить?",
        "en": "What would you like to change?",
    },
    "settings_language_btn": {
        "uz": "🌐 Tilni o'zgartirish",
        "ru": "🌐 Изменить язык",
        "en": "🌐 Change language",
    },
    "settings_address_btn": {
        "uz": "📍 Manzilni o'zgartirish",
        "ru": "📍 Изменить адрес",
        "en": "📍 Change address",
    },
    "settings_name_btn": {
        "uz": "✏️ Ismni o'zgartirish",
        "ru": "✏️ Изменить имя",
        "en": "✏️ Change name",
    },
    "enter_new_name": {
        "uz": "Yangi ismingizni kiriting:",
        "ru": "Введите новое имя:",
        "en": "Enter your new name:",
    },
    "saved": {"uz": "✅ Saqlandi.", "ru": "✅ Сохранено.", "en": "✅ Saved."},
    "no_access": {
        "uz": "⛔ Sizda bu buyruq uchun ruxsat yo'q.",
        "ru": "⛔ У вас нет доступа к этой команде.",
        "en": "⛔ You don't have access to this command.",
    },
    "banned": {
        "uz": "⛔ Siz botdan bloklangansiz.",
        "ru": "⛔ Вы заблокированы в этом боте.",
        "en": "⛔ You are banned from this bot.",
    },
    "help_user": {
        "uz": (
            "🛍 <b>Online Market bot</b>\n\n"
            "/start — botni boshlash\n"
            "/help — yordam\n\n"
            "Menyudan foydalanib xarid qiling, savatni boshqaring, "
            "profil va sozlamalarni ko'ring."
        ),
        "ru": (
            "🛍 <b>Online Market bot</b>\n\n"
            "/start — начать\n"
            "/help — помощь\n\n"
            "Используйте меню для покупок, управления корзиной, "
            "просмотра профиля и настроек."
        ),
        "en": (
            "🛍 <b>Online Market bot</b>\n\n"
            "/start — start the bot\n"
            "/help — help\n\n"
            "Use the menu to shop, manage your cart, and view your "
            "profile and settings."
        ),
    },
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    entry = LEXICON_TEXT.get(key, {})
    template = entry.get(lang) or entry.get("uz") or key
    return template.format(**kwargs) if kwargs else template


# Telegramning chap tomondagi "Menu" (/ tugmasi) ro'yxatida ko'rinadigan
# oddiy foydalanuvchi komandalari. Har bir til uchun (buyruq, tavsif) juftligi.
# Ishlatilishi: bot.set_my_commands(...) — bot/utils/commands.py ga qarang.
LEXICON_COMMANDS_USER: dict[str, list[tuple[str, str]]] = {
    "uz": [
        ("start", "Botni ishga tushirish"),
        ("help", "Yordam va buyruqlar ro'yxati"),
    ],
    "ru": [
        ("start", "Запустить бота"),
        ("help", "Помощь и список команд"),
    ],
    "en": [
        ("start", "Start the bot"),
        ("help", "Help and command list"),
    ],
}
