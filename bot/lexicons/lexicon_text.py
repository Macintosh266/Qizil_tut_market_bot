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
    "bot_intro": {
        "uz": (
            "🌳 <b>QIZIL TUT | BARAKA</b>\n"
            "<i>Halol savdo</i>\n\n"
            "Assalomu alaykum va botimizga xush kelibsiz! 👋\n\n"
            "<b>Qizil Tut</b> — bu sizga eng yaqin do'konlardan kerakli "
            "mahsulotlarni qulay tarzda buyurtma qilish imkonini beruvchi "
            "onlayn-do'kon botidir.\n\n"
            "Bot orqali siz:\n"
            "🏪 Yaqiningizdagi do'konlarni tanlashingiz\n"
            "🛍 Mahsulotlarni kategoriya bo'yicha ko'rib chiqishingiz yoki qidirishingiz\n"
            "🛒 Savatga qo'shib, kerakli miqdorni belgilashingiz\n"
            "🚚 Yetkazib berish yoki o'zingiz olib ketishni tanlashingiz\n"
            "📦 Buyurtmangiz holatini kuzatib borishingiz\n\n"
            "mumkin — barchasi bitta bot ichida, tez va qulay."
        ),
        "ru": (
            "🌳 <b>QIZIL TUT | BARAKA</b>\n"
            "<i>Честная торговля</i>\n\n"
            "Здравствуйте и добро пожаловать в наш бот! 👋\n\n"
            "<b>Qizil Tut</b> — это бот онлайн-магазина, который позволяет "
            "удобно заказывать нужные товары из ближайших к вам магазинов.\n\n"
            "С помощью бота вы можете:\n"
            "🏪 Выбрать ближайший к вам магазин\n"
            "🛍 Просматривать товары по категориям или искать нужный товар\n"
            "🛒 Добавлять в корзину и указывать нужное количество\n"
            "🚚 Выбрать доставку или самовывоз\n"
            "📦 Отслеживать статус своего заказа\n\n"
            "— всё это в одном боте, быстро и удобно."
        ),
        "en": (
            "🌳 <b>QIZIL TUT | BARAKA</b>\n"
            "<i>Honest trade</i>\n\n"
            "Hello and welcome to our bot! 👋\n\n"
            "<b>Qizil Tut</b> is an online store bot that lets you conveniently "
            "order the products you need from the store nearest to you.\n\n"
            "With this bot you can:\n"
            "🏪 Choose the store nearest to you\n"
            "🛍 Browse products by category or search for what you need\n"
            "🛒 Add items to your cart and set the quantity you need\n"
            "🚚 Choose delivery or pickup\n"
            "📦 Track the status of your order\n\n"
            "— all in one bot, fast and convenient."
        ),
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
    "menu_feedback": {"uz": "💬 Fikr bildirish", "ru": "💬 Оставить отзыв", "en": "💬 Give feedback"},
    "feedback_prompt": {
        "uz": "✍️ Fikr, taklif yoki shikoyatingizni yozib qoldiring:",
        "ru": "✍️ Напишите ваш отзыв, предложение или жалобу:",
        "en": "✍️ Please write your feedback, suggestion, or complaint:",
    },
    "feedback_sent": {
        "uz": "✅ Rahmat! Fikringiz qabul qilindi.",
        "ru": "✅ Спасибо! Ваш отзыв принят.",
        "en": "✅ Thank you! Your feedback has been received.",
    },
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
    "market_empty": {
        "uz": "😔 Afsuski, bu do'konda hozircha birorta ham mahsulot yo'q.",
        "ru": "😔 К сожалению, в этом магазине пока нет ни одного товара.",
        "en": "😔 Unfortunately, this market has no products yet.",
    },
    "choose_category": {
        "uz": "Kategoriyani tanlang:",
        "ru": "Выберите категорию:",
        "en": "Choose a category:",
    },
    "choose_brand": {
        "uz": "Brendni tanlang:",
        "ru": "Выберите бренд:",
        "en": "Choose a brand:",
    },
    "all_products_btn": {
        "uz": "📋 Barcha mahsulotlar",
        "ru": "📋 Все товары",
        "en": "📋 All products",
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
    "product_not_found": {
        "uz": "Bu mahsulot topilmadi (ehtimol o'chirilgan).",
        "ru": "Товар не найден (возможно, он был удалён).",
        "en": "This product was not found (it may have been removed).",
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
    "cart_qty_prompt": {
        "uz": "🔢 <b>{name}</b> uchun yangi sonni kiriting (0 — mahsulotni savatdan o'chiradi):",
        "ru": "🔢 Введите новое количество для <b>{name}</b> (0 — удалит товар из корзины):",
        "en": "🔢 Enter the new quantity for <b>{name}</b> (0 removes it from the cart):",
    },
    "product_qty_prompt": {
        "uz": "🔢 <b>{name}</b> dan nechta olishni xohlaysiz? Sonni yozing (kamida 1):",
        "ru": "🔢 Сколько штук <b>{name}</b> вы хотите взять? Введите число (не менее 1):",
        "en": "🔢 How many of <b>{name}</b> would you like? Enter a number (at least 1):",
    },
    "only_numbers": {
        "uz": "❗️ Iltimos, faqat son kiriting.",
        "ru": "❗️ Пожалуйста, введите только число.",
        "en": "❗️ Please enter a number only.",
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
        "uz": "📦 Buyurtmangiz #{order_id} qabul qilindi va ko'rib chiqilmoqda. Tasdiqlangach sizga xabar beramiz.",
        "ru": "📦 Ваш заказ #{order_id} принят и находится на рассмотрении. Мы сообщим вам, как только он будет подтверждён.",
        "en": "📦 Your order #{order_id} has been received and is being reviewed. We'll notify you once it's confirmed.",
    },
    "order_canceled": {
        "uz": "❌ Buyurtma bekor qilindi.",
        "ru": "❌ Заказ отменён.",
        "en": "❌ Order canceled.",
    },
    "order_accepted_customer": {
        "uz": "✅ Buyurtmangiz #{order_id} qabul qilindi! Tez orada siz bilan bog'lanishadi.",
        "ru": "✅ Ваш заказ #{order_id} принят! С вами скоро свяжутся.",
        "en": "✅ Your order #{order_id} has been accepted! We'll contact you shortly.",
    },
    "order_rejected_customer": {
        "uz": "❌ Afsuski, buyurtmangiz #{order_id} rad etildi.",
        "ru": "❌ К сожалению, ваш заказ #{order_id} отклонён.",
        "en": "❌ Unfortunately, your order #{order_id} has been rejected.",
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
            "🛍 <b>Qizil Tut | Baraka</b>\n\n"
            "/start — botni qayta boshlash\n"
            "/help — yordam\n\n"
            "Pastdagi menyudan foydalaning: mahsulot xarid qiling, savatni "
            "boshqaring, buyurtma bering, profil va sozlamalaringizni ko'ring, "
            "yoki bizga fikr-mulohaza qoldiring."
        ),
        "ru": (
            "🛍 <b>Qizil Tut | Baraka</b>\n\n"
            "/start — перезапустить бота\n"
            "/help — помощь\n\n"
            "Используйте меню ниже: покупайте товары, управляйте корзиной, "
            "оформляйте заказ, смотрите профиль и настройки, а также "
            "оставляйте нам отзывы."
        ),
        "en": (
            "🛍 <b>Qizil Tut | Baraka</b>\n\n"
            "/start — restart the bot\n"
            "/help — help\n\n"
            "Use the menu below: shop for products, manage your cart, "
            "place an order, view your profile and settings, or leave "
            "us feedback."
        ),
    },
    "help_admin": {
        "uz": (
            "🛠 <b>Admin panel — yordam</b>\n\n"
            "/start — botni qayta boshlash\n"
            "/help — yordam\n\n"
            "Admin panel orqali quyidagilarni boshqarasiz:\n"
            "📦 <b>Mahsulotlar</b> — qo'shish, tahrirlash, o'chirish, ro'yxat\n"
            "🗂 <b>Kategoriyalar</b> va 🏷 <b>Brendlar</b> — qo'shish/o'chirish\n"
            "🏪 <b>Do'konlar</b> va 👤 <b>Adminlar</b> — faqat super-admin uchun\n"
            "🚫 <b>Ban</b> — foydalanuvchini bloklash/blokdan chiqarish\n"
            "📊 <b>Statistika</b> — davr bo'yicha savdo hisobotlari\n"
            "💬 <b>Fikrlar</b> — mijozlar qoldirgan fikr-mulohazalar\n\n"
            "Yangi buyurtma tushganda sizga xabar keladi — 'Qabul qilish' "
            "yoki 'Rad etish' tugmasi orqali javob bering."
        ),
        "ru": (
            "🛠 <b>Панель администратора — помощь</b>\n\n"
            "/start — перезапустить бота\n"
            "/help — помощь\n\n"
            "Через админ-панель вы управляете:\n"
            "📦 <b>Товарами</b> — добавление, редактирование, удаление, список\n"
            "🗂 <b>Категориями</b> и 🏷 <b>Брендами</b> — добавление/удаление\n"
            "🏪 <b>Магазинами</b> и 👤 <b>Админами</b> — только для супер-админа\n"
            "🚫 <b>Баном</b> — блокировка/разблокировка пользователей\n"
            "📊 <b>Статистикой</b> — отчёты о продажах за период\n"
            "💬 <b>Отзывами</b> — отзывы, оставленные клиентами\n\n"
            "При поступлении нового заказа вам придёт уведомление — "
            "ответьте кнопкой «Принять» или «Отклонить»."
        ),
        "en": (
            "🛠 <b>Admin panel — help</b>\n\n"
            "/start — restart the bot\n"
            "/help — help\n\n"
            "Through the admin panel you manage:\n"
            "📦 <b>Products</b> — add, edit, delete, list\n"
            "🗂 <b>Categories</b> and 🏷 <b>Brands</b> — add/delete\n"
            "🏪 <b>Markets</b> and 👤 <b>Admins</b> — super-admin only\n"
            "🚫 <b>Ban</b> — block/unblock users\n"
            "📊 <b>Statistics</b> — sales reports by period\n"
            "💬 <b>Feedback</b> — messages left by customers\n\n"
            "You'll be notified of new orders — reply using the "
            "'Accept' or 'Reject' button."
        ),
    },
    "unknown_command": {
        "uz": "🤔 Bunday buyruq yoki xabar mavjud emas. Menyudan foydalaning yoki /help buyrug'ini yuboring.",
        "ru": "🤔 Такой команды или сообщения не существует. Используйте меню или отправьте /help.",
        "en": "🤔 No such command or message. Please use the menu or send /help.",
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