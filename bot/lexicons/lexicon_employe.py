"""Admin/ishchi panel uchun tarjimalar — asosiy lexicon_text.py dan alohida,
chunki bu matnlar faqat admin/ishchi menyularida ishlatiladi."""

LEXICON_EMPLOYE: dict[str, dict[str, str]] = {
    # ========== ASOSIY MENYU ==========
    "admin_menu": {
        "uz": "🛠 Admin panel",
        "ru": "🛠 Панель администратора",
        "en": "🛠 Admin panel",
    },
    "staff_menu": {
        "uz": "👷 Ishchi panel",
        "ru": "👷 Панель сотрудника",
        "en": "👷 Staff panel",
    },
    "admin_panel_welcome": {
        "uz": "👋 Admin panelga xush kelibsiz!",
        "ru": "👋 Добро пожаловать в панель администратора!",
        "en": "👋 Welcome to admin panel!",
    },
    "staff_panel_welcome": {
        "uz": "👋 Ishchi panelga xush kelibsiz!",
        "ru": "👋 Добро пожаловать в панель сотрудника!",
        "en": "👋 Welcome to staff panel!",
    },

    # ========== ADMIN PANEL TUGMALARI ==========
    "admin_panel_btn": {
        "uz": "🛠 Admin panel",
        "ru": "🛠 Панель администратора",
        "en": "🛠 Admin panel",
    },
    "admin_management_btn": {
        "uz": "👥 Admin boshqaruvi",
        "ru": "👥 Управление администраторами",
        "en": "👥 Admin management",
    },
    "staff_management_btn": {
        "uz": "👤 Staff boshqaruvi",
        "ru": "👤 Управление сотрудниками",
        "en": "👤 Staff management",
    },
    "ban_management_btn": {
        "uz": "🚫 Ban/Unban",
        "ru": "🚫 Бан/Разбан",
        "en": "🚫 Ban/Unban",
    },
    "market_management_btn": {
        "uz": "🏪 Do'kon boshqaruvi",
        "ru": "🏪 Управление магазинами",
        "en": "🏪 Market management",
    },
    "product_management_btn": {
        "uz": "📦 Mahsulot boshqaruvi",
        "ru": "📦 Управление товарами",
        "en": "📦 Product management",
    },
    "statistics_btn": {
        "uz": "📊 Statistika",
        "ru": "📊 Статистика",
        "en": "📊 Statistics",
    },
    "back_btn": {
        "uz": "🔙 Orqaga",
        "ru": "🔙 Назад",
        "en": "🔙 Back",
    },

    # ========== ADMIN BOSHQARUVI TUGMALARI ==========
    "add_admin_btn": {
        "uz": "➕ Admin qo'shish",
        "ru": "➕ Добавить администратора",
        "en": "➕ Add admin",
    },
    "delete_admin_btn": {
        "uz": "➖ Admin o'chirish",
        "ru": "➖ Удалить администратора",
        "en": "➖ Remove admin",
    },
    "admin_list_btn": {
        "uz": "📋 Adminlar ro'yxati",
        "ru": "📋 Список администраторов",
        "en": "📋 Admin list",
    },
    "add_admin_prompt": {
        "uz": "Admin qo'shish uchun foydalanuvchi ID yoki @username kiriting:",
        "ru": "Введите ID пользователя или @username для добавления администратора:",
        "en": "Enter user ID or @username to add admin:",
    },
    "delete_admin_prompt": {
        "uz": "Admin o'chirish uchun foydalanuvchi ID yoki @username kiriting:",
        "ru": "Введите ID пользователя или @username для удаления администратора:",
        "en": "Enter user ID or @username to remove admin:",
    },

    # ========== STAFF BOSHQARUVI TUGMALARI ==========
    "add_staff_btn": {
        "uz": "➕ Staff qo'shish",
        "ru": "➕ Добавить сотрудника",
        "en": "➕ Add staff",
    },
    "delete_staff_btn": {
        "uz": "➖ Staff o'chirish",
        "ru": "➖ Удалить сотрудника",
        "en": "➖ Remove staff",
    },
    "staff_list_btn": {
        "uz": "📋 Staff ro'yxati",
        "ru": "📋 Список сотрудников",
        "en": "📋 Staff list",
    },
    "add_staff_prompt": {
        "uz": "Staff qo'shish uchun foydalanuvchi ID yoki @username kiriting:",
        "ru": "Введите ID пользователя или @username для добавления сотрудника:",
        "en": "Enter user ID or @username to add staff:",
    },
    "delete_staff_prompt": {
        "uz": "Staff o'chirish uchun foydalanuvchi ID yoki @username kiriting:",
        "ru": "Введите ID пользователя или @username для удаления сотрудника:",
        "en": "Enter user ID or @username to remove staff:",
    },

    # ========== BAN/UNBAN TUGMALARI ==========
    "ban_user_btn": {
        "uz": "🚫 Foydalanuvchini bloklash",
        "ru": "🚫 Заблокировать пользователя",
        "en": "🚫 Ban user",
    },
    "unban_user_btn": {
        "uz": "✅ Foydalanuvchini blokdan chiqarish",
        "ru": "✅ Разблокировать пользователя",
        "en": "✅ Unban user",
    },
    "ban_user_prompt": {
        "uz": "Bloklash uchun foydalanuvchi ID yoki @username kiriting:",
        "ru": "Введите ID пользователя или @username для блокировки:",
        "en": "Enter user ID or @username to ban:",
    },
    "unban_user_prompt": {
        "uz": "Blokdan chiqarish uchun foydalanuvchi ID yoki @username kiriting:",
        "ru": "Введите ID пользователя или @username для разблокировки:",
        "en": "Enter user ID or @username to unban:",
    },

    # ========== MARKET BOSHQARUVI TUGMALARI ==========
    "add_market_btn": {
        "uz": "🏪 Do'kon qo'shish",
        "ru": "🏪 Добавить магазин",
        "en": "🏪 Add market",
    },
    "delete_market_btn": {
        "uz": "🗑️ Do'kon o'chirish",
        "ru": "🗑️ Удалить магазин",
        "en": "🗑️ Delete market",
    },
    "market_list_btn": {
        "uz": "📋 Do'konlar ro'yxati",
        "ru": "📋 Список магазинов",
        "en": "📋 Market list",
    },
    "add_market_prompt": {
        "uz": "Yangi do'kon nomini kiriting:",
        "ru": "Введите название нового магазина:",
        "en": "Enter new market name:",
    },
    "add_market_address_prompt": {
        "uz": "Do'kon manzilini kiriting:",
        "ru": "Введите адрес магазина:",
        "en": "Enter market address:",
    },
    "delete_market_prompt": {
        "uz": "O'chirish uchun do'kon nomini kiriting:",
        "ru": "Введите название магазина для удаления:",
        "en": "Enter market name to delete:",
    },
    "market_name_exists": {
        "uz": "❌ Bu nomdagi do'kon allaqachon mavjud!",
        "ru": "❌ Магазин с таким названием уже существует!",
        "en": "❌ Market with this name already exists!",
    },

    # ========== PRODUCT BOSHQARUVI TUGMALARI ==========
    "add_product_btn": {
        "uz": "📦 Mahsulot qo'shish",
        "ru": "📦 Добавить товар",
        "en": "📦 Add product",
    },
    "delete_product_btn": {
        "uz": "🗑️ Mahsulot o'chirish",
        "ru": "🗑️ Удалить товар",
        "en": "🗑️ Delete product",
    },
    "product_list_btn": {
        "uz": "📋 Mahsulotlar ro'yxati",
        "ru": "📋 Список товаров",
        "en": "📋 Product list",
    },
    "edit_product_price_btn": {
        "uz": "✏️ Mahsulotni tahrirlash",
        "ru": "✏️ Редактировать товар",
        "en": "✏️ Edit product",
    },
    "add_product_name_prompt": {
        "uz": "Mahsulot nomini kiriting:",
        "ru": "Введите название товара:",
        "en": "Enter product name:",
    },
    "add_product_price_prompt": {
        "uz": "Mahsulot narxini kiriting (faqat raqam):",
        "ru": "Введите цену товара (только число):",
        "en": "Enter product price (only number):",
    },
    "add_product_qty_prompt": {
        "uz": "Mahsulotdan nechta bor? (son kiriting):",
        "ru": "Сколько единиц товара в наличии? (введите число):",
        "en": "How many units are in stock? (enter a number):",
    },
    "add_product_category_prompt": {
        "uz": "Yangi kategoriya nomini kiriting:",
        "ru": "Введите название новой категории:",
        "en": "Enter the new category name:",
    },
    "choose_category_prompt": {
        "uz": "📂 Mahsulot uchun kategoriyani tanlang:",
        "ru": "📂 Выберите категорию для товара:",
        "en": "📂 Choose a category for the product:",
    },
    "add_new_category_btn": {
        "uz": "➕ Yangi kategoriya",
        "ru": "➕ Новая категория",
        "en": "➕ New category",
    },
    "choose_brand_prompt": {
        "uz": "🏷 Mahsulot uchun brendni tanlang:",
        "ru": "🏷 Выберите бренд для товара:",
        "en": "🏷 Choose a brand for the product:",
    },
    "no_brand_btn": {
        "uz": "🚫 Brendsiz",
        "ru": "🚫 Без бренда",
        "en": "🚫 No brand",
    },
    "add_new_brand_btn": {
        "uz": "➕ Yangi brend",
        "ru": "➕ Новый бренд",
        "en": "➕ New brand",
    },
    "add_product_photo_prompt": {
        "uz": "Mahsulot rasmini yuboring (o'tkazib yuborish uchun '-' yozing):",
        "ru": "Отправьте фото товара (чтобы пропустить, напишите '-'):",
        "en": "Send a product photo (send '-' to skip):",
    },

    # ========== KATEGORIYA BOSHQARUVI (alohida bo'lim) ==========
    "category_management_btn": {
        "uz": "🗂 Kategoriyalar",
        "ru": "🗂 Категории",
        "en": "🗂 Categories",
    },
    "add_category_btn": {
        "uz": "➕ Kategoriya qo'shish",
        "ru": "➕ Добавить категорию",
        "en": "➕ Add category",
    },
    "delete_category_btn": {
        "uz": "🗑 Kategoriya o'chirish",
        "ru": "🗑 Удалить категорию",
        "en": "🗑 Delete category",
    },
    "category_list_btn": {
        "uz": "📋 Kategoriyalar ro'yxati",
        "ru": "📋 Список категорий",
        "en": "📋 Category list",
    },
    "add_category_prompt": {
        "uz": "Yangi kategoriya nomini kiriting:",
        "ru": "Введите название новой категории:",
        "en": "Enter the new category name:",
    },
    "category_added": {
        "uz": "✅ '{name}' kategoriyasi qo'shildi.",
        "ru": "✅ Категория '{name}' добавлена.",
        "en": "✅ Category '{name}' added.",
    },
    "category_exists": {
        "uz": "❗️ Bu nomdagi kategoriya allaqachon mavjud.",
        "ru": "❗️ Категория с таким названием уже существует.",
        "en": "❗️ A category with this name already exists.",
    },
    "no_categories": {
        "uz": "Hozircha kategoriyalar yo'q. Avval kategoriya qo'shing.",
        "ru": "Пока нет категорий. Сначала добавьте категорию.",
        "en": "There are no categories yet. Please add one first.",
    },
    "category_has_products": {
        "uz": "❗️ Bu kategoriyada mahsulotlar mavjud. Avval ularni boshqa kategoriyaga o'tkazing yoki o'chiring.",
        "ru": "❗️ В этой категории есть товары. Сначала перенесите их в другую категорию или удалите.",
        "en": "❗️ This category still has products. Move or delete them first.",
    },
    "confirm_delete_category": {
        "uz": "'{name}' kategoriyasini o'chirishni tasdiqlaysizmi?",
        "ru": "Подтвердите удаление категории '{name}'?",
        "en": "Confirm deleting the category '{name}'?",
    },
    "category_deleted": {
        "uz": "🗑 '{name}' kategoriyasi o'chirildi.",
        "ru": "🗑 Категория '{name}' удалена.",
        "en": "🗑 Category '{name}' deleted.",
    },

    # ========== BREND BOSHQARUVI (alohida bo'lim) ==========
    "brand_management_btn": {
        "uz": "🏷 Brendlar",
        "ru": "🏷 Бренды",
        "en": "🏷 Brands",
    },
    "add_brand_btn": {
        "uz": "➕ Brend qo'shish",
        "ru": "➕ Добавить бренд",
        "en": "➕ Add brand",
    },
    "delete_brand_btn": {
        "uz": "🗑 Brend o'chirish",
        "ru": "🗑 Удалить бренд",
        "en": "🗑 Delete brand",
    },
    "brand_list_btn": {
        "uz": "📋 Brendlar ro'yxati",
        "ru": "📋 Список брендов",
        "en": "📋 Brand list",
    },
    "add_brand_prompt": {
        "uz": "Yangi brend nomini kiriting:",
        "ru": "Введите название нового бренда:",
        "en": "Enter the new brand name:",
    },
    "brand_added": {
        "uz": "✅ '{name}' brendi qo'shildi.",
        "ru": "✅ Бренд '{name}' добавлен.",
        "en": "✅ Brand '{name}' added.",
    },
    "brand_exists": {
        "uz": "❗️ Bu nomdagi brend allaqachon mavjud.",
        "ru": "❗️ Бренд с таким названием уже существует.",
        "en": "❗️ A brand with this name already exists.",
    },
    "no_brands": {
        "uz": "Hozircha brendlar yo'q.",
        "ru": "Пока нет брендов.",
        "en": "There are no brands yet.",
    },
    "confirm_delete_brand": {
        "uz": "'{name}' brendini o'chirishni tasdiqlaysizmi? (bu brenddagi mahsulotlar 'brendsiz' bo'lib qoladi)",
        "ru": "Подтвердите удаление бренда '{name}'? (товары этого бренда останутся без бренда)",
        "en": "Confirm deleting the brand '{name}'? (its products will become brand-less)",
    },
    "brand_deleted": {
        "uz": "🗑 '{name}' brendi o'chirildi.",
        "ru": "🗑 Бренд '{name}' удалён.",
        "en": "🗑 Brand '{name}' deleted.",
    },

    # ========== FIKR-MULOHAZALAR (admin ko'rinishi) ==========
    "feedback_management_btn": {
        "uz": "💬 Fikrlar",
        "ru": "💬 Отзывы",
        "en": "💬 Feedback",
    },
    "feedback_empty": {
        "uz": "Hozircha fikrlar yo'q.",
        "ru": "Пока нет отзывов.",
        "en": "There is no feedback yet.",
    },
    "feedback_view": {
        "uz": "💬 Fikr {index}/{total}\n👤 {name}{username}\n\n{text}\n\n{status}",
        "ru": "💬 Отзыв {index}/{total}\n👤 {name}{username}\n\n{text}\n\n{status}",
        "en": "💬 Feedback {index}/{total}\n👤 {name}{username}\n\n{text}\n\n{status}",
    },
    "feedback_status_new": {
        "uz": "🆕 Ko'rilmagan",
        "ru": "🆕 Не просмотрено",
        "en": "🆕 Unreviewed",
    },
    "feedback_status_reviewed": {
        "uz": "✅ Ko'rib chiqilgan",
        "ru": "✅ Просмотрено",
        "en": "✅ Reviewed",
    },
    "mark_reviewed_btn": {
        "uz": "✅ Ko'rib chiqildi deb belgilash",
        "ru": "✅ Отметить как просмотренное",
        "en": "✅ Mark as reviewed",
    },
    "feedback_marked_reviewed": {
        "uz": "✅ Ko'rib chiqilgan deb belgilandi.",
        "ru": "✅ Отмечено как просмотренное.",
        "en": "✅ Marked as reviewed.",
    },
    "close_btn": {
        "uz": "✖️ Yopish",
        "ru": "✖️ Закрыть",
        "en": "✖️ Close",
    },
    "choose_market_prompt": {
        "uz": "Do'konni tanlang:",
        "ru": "Выберите магазин:",
        "en": "Choose a market:",
    },
    "choose_product_prompt": {
        "uz": "Mahsulotni tanlang:",
        "ru": "Выберите товар:",
        "en": "Choose a product:",
    },
    "choose_admin_prompt": {
        "uz": "Adminni tanlang:",
        "ru": "Выберите администратора:",
        "en": "Choose an admin:",
    },
    "choose_staff_prompt": {
        "uz": "Ishchini tanlang:",
        "ru": "Выберите сотрудника:",
        "en": "Choose a staff member:",
    },
    "choose_banned_prompt": {
        "uz": "Blokdan chiqariladigan foydalanuvchini tanlang:",
        "ru": "Выберите пользователя для разблокировки:",
        "en": "Choose a user to unban:",
    },
    "search_or_choose_hint": {
        "uz": "\n\n🔍 Yoki nomini/ID'sini/username'ini yozib qidiring.",
        "ru": "\n\n🔍 Или напишите имя/ID/username для поиска.",
        "en": "\n\n🔍 Or type a name/ID/username to search.",
    },
    "no_results": {
        "uz": "❌ Hech narsa topilmadi. Boshqa so'z bilan qidiring.",
        "ru": "❌ Ничего не найдено. Попробуйте другой запрос.",
        "en": "❌ Nothing found. Try a different search.",
    },
    "add_product_market_prompt": {
        "uz": "Qaysi do'konga qo'shish kerak? Do'kon nomini kiriting:",
        "ru": "В какой магазин добавить? Введите название магазина:",
        "en": "Which market to add? Enter market name:",
    },
    "delete_product_prompt": {
        "uz": "O'chirish uchun mahsulot nomini kiriting:",
        "ru": "Введите название товара для удаления:",
        "en": "Enter product name to delete:",
    },
    "edit_product_price_prompt": {
        "uz": "Narxini o'zgartirish uchun mahsulot nomini kiriting:",
        "ru": "Введите название товара для изменения цены:",
        "en": "Enter product name to edit price:",
    },
    "edit_product_new_price_prompt": {
        "uz": "Yangi narxni kiriting (faqat raqam):",
        "ru": "Введите новую цену (только число):",
        "en": "Enter new price (only number):",
    },
    "choose_field_to_edit": {
        "uz": "Nimani o'zgartirmoqchisiz?",
        "ru": "Что хотите изменить?",
        "en": "What would you like to change?",
    },
    "edit_field_name_btn": {
        "uz": "📝 Nomi",
        "ru": "📝 Название",
        "en": "📝 Name",
    },
    "edit_field_description_btn": {
        "uz": "📄 Tavsifi",
        "ru": "📄 Описание",
        "en": "📄 Description",
    },
    "edit_field_price_btn": {
        "uz": "💰 Narxi",
        "ru": "💰 Цена",
        "en": "💰 Price",
    },
    "edit_field_stock_btn": {
        "uz": "📦 Miqdori",
        "ru": "📦 Количество",
        "en": "📦 Stock",
    },
    "edit_field_category_btn": {
        "uz": "🗂 Kategoriyasi",
        "ru": "🗂 Категория",
        "en": "🗂 Category",
    },
    "edit_field_photo_btn": {
        "uz": "🖼 Rasmi",
        "ru": "🖼 Фото",
        "en": "🖼 Photo",
    },
    "edit_new_name_prompt": {
        "uz": "Yangi nomini kiriting:",
        "ru": "Введите новое название:",
        "en": "Enter the new name:",
    },
    "edit_new_description_prompt": {
        "uz": "Yangi tavsifni kiriting:",
        "ru": "Введите новое описание:",
        "en": "Enter the new description:",
    },
    "edit_new_stock_prompt": {
        "uz": "Yangi miqdorni kiriting (faqat raqam):",
        "ru": "Введите новое количество (только число):",
        "en": "Enter the new stock quantity (number only):",
    },
    "edit_new_category_prompt": {
        "uz": "Yangi kategoriya nomini kiriting:",
        "ru": "Введите новое название категории:",
        "en": "Enter the new category name:",
    },
    "edit_new_photo_prompt": {
        "uz": "Yangi rasmni yuboring:",
        "ru": "Отправьте новое фото:",
        "en": "Send the new photo:",
    },
    "product_name_updated": {
        "uz": "✅ Nomi '{name}' ga o'zgartirildi.",
        "ru": "✅ Название изменено на '{name}'.",
        "en": "✅ Name updated to '{name}'.",
    },
    "product_description_updated": {
        "uz": "✅ Tavsif yangilandi.",
        "ru": "✅ Описание обновлено.",
        "en": "✅ Description updated.",
    },
    "product_stock_updated": {
        "uz": "✅ Miqdor {stock} ga o'zgartirildi.",
        "ru": "✅ Количество изменено на {stock}.",
        "en": "✅ Stock updated to {stock}.",
    },
    "product_category_updated": {
        "uz": "✅ Kategoriya '{name}' ga o'zgartirildi.",
        "ru": "✅ Категория изменена на '{name}'.",
        "en": "✅ Category updated to '{name}'.",
    },
    "product_photo_updated": {
        "uz": "✅ Rasm yangilandi.",
        "ru": "✅ Фото обновлено.",
        "en": "✅ Photo updated.",
    },
    "product_restocked": {
        "uz": "ℹ️ '{name}' allaqachon mavjud edi — miqdori {stock} donaga oshirildi (endi jami: {total}).",
        "ru": "ℹ️ '{name}' уже существовал — количество увеличено на {stock} (итого: {total}).",
        "en": "ℹ️ '{name}' already existed — stock increased by {stock} (total now: {total}).",
    },
    "product_price_updated": {
        "uz": "✅ '{name}' mahsulotining narxi {price} so'mga o'zgartirildi.",
        "ru": "✅ Цена товара '{name}' изменена на {price} сум.",
        "en": "✅ Product '{name}' price updated to {price} sum.",
    },
    "product_not_found_in_market": {
        "uz": "❌ Bu do'konda bunday mahsulot topilmadi!",
        "ru": "❌ В этом магазине такой товар не найден!",
        "en": "❌ Product not found in this market!",
    },

    # ========== UMUMIY MATNLAR ==========
    "usage": {
        "uz": "Foydalanish: {usage}",
        "ru": "Использование: {usage}",
        "en": "Usage: {usage}",
    },
    "user_not_found": {
        "uz": "❌ Foydalanuvchi topilmadi.",
        "ru": "❌ Пользователь не найден.",
        "en": "❌ User not found.",
    },
    "admin_added": {
        "uz": "✅ {name} admin etib tayinlandi.",
        "ru": "✅ {name} назначен администратором.",
        "en": "✅ {name} is now an admin.",
    },
    "admin_removed": {
        "uz": "✅ {name} adminlikdan olindi.",
        "ru": "✅ {name} снят с должности администратора.",
        "en": "✅ {name} is no longer an admin.",
    },
    "admin_not_found": {
        "uz": "❌ Admin topilmadi.",
        "ru": "❌ Администратор не найден.",
        "en": "❌ Admin not found.",
    },
    "staff_added": {
        "uz": "✅ {name} ishchi etib tayinlandi.",
        "ru": "✅ {name} назначен сотрудником.",
        "en": "✅ {name} is now staff.",
    },
    "staff_removed": {
        "uz": "✅ {name} ishchilikdan olindi.",
        "ru": "✅ {name} снят с должности сотрудника.",
        "en": "✅ {name} is no longer staff.",
    },
    "staff_not_found": {
        "uz": "❌ Staff topilmadi.",
        "ru": "❌ Сотрудник не найден.",
        "en": "❌ Staff not found.",
    },
    "user_banned": {
        "uz": "🚫 {name} bloklandi.",
        "ru": "🚫 {name} заблокирован.",
        "en": "🚫 {name} has been banned.",
    },
    "user_unbanned": {
        "uz": "✅ {name} blokdan chiqarildi.",
        "ru": "✅ {name} разблокирован.",
        "en": "✅ {name} has been unbanned.",
    },
    "user_already_banned": {
        "uz": "ℹ️ {name} allaqachon bloklangan.",
        "ru": "ℹ️ {name} уже заблокирован.",
        "en": "ℹ️ {name} is already banned.",
    },
    "user_not_banned": {
        "uz": "ℹ️ {name} bloklanmagan.",
        "ru": "ℹ️ {name} не заблокирован.",
        "en": "ℹ️ {name} is not banned.",
    },
    "super_admin_ban":{
        "uz":"Siz super adminni ban qila olmaysiz",
        "ru":"Вы не можете заблокировать суперадминистратора.",
        "en":"You cannot ban super admin.",
    },
    "market_added": {
        "uz": "✅ '{name}' do'koni qo'shildi.",
        "ru": "✅ Магазин '{name}' добавлен.",
        "en": "✅ Market '{name}' added.",
    },
    "market_deleted": {
        "uz": "✅ '{name}' do'koni o'chirildi.",
        "ru": "✅ Магазин '{name}' удалён.",
        "en": "✅ Market '{name}' deleted.",
    },
    "market_not_found": {
        "uz": "❌ Do'kon topilmadi.",
        "ru": "❌ Магазин не найден.",
        "en": "❌ Market not found.",
    },
    "product_added": {
        "uz": "✅ '{name}' mahsuloti {price} so'm narxda qo'shildi.",
        "ru": "✅ Товар '{name}' добавлен по цене {price} сум.",
        "en": "✅ Product '{name}' added for {price} sum.",
    },
    "product_deleted": {
        "uz": "✅ '{name}' mahsuloti o'chirildi.",
        "ru": "✅ Товар '{name}' удалён.",
        "en": "✅ Product '{name}' deleted.",
    },
    "product_not_found": {
        "uz": "❌ Mahsulot topilmadi.",
        "ru": "❌ Товар не найден.",
        "en": "❌ Product not found.",
    },

    # ========== BUYURTMA MATNLARI ==========
    "new_order_notify": {
        "uz": "🆕 Yangi buyurtma #{order_id}\nMijoz: {name}\nTelefon: {phone}\n\n📦 Mahsulotlar:\n{items}\n\nSumma: {total}",
        "ru": "🆕 Новый заказ #{order_id}\nКлиент: {name}\nТелефон: {phone}\n\n📦 Товары:\n{items}\n\nСумма: {total}",
        "en": "🆕 New order #{order_id}\nCustomer: {name}\nPhone: {phone}\n\n📦 Items:\n{items}\n\nTotal: {total}",
    },
    "accept_order_btn": {
        "uz": "✅ Qabul qilish",
        "ru": "✅ Принять",
        "en": "✅ Accept",
    },
    "reject_order_btn": {
        "uz": "❌ Rad etish",
        "ru": "❌ Отклонить",
        "en": "❌ Reject",
    },
    "order_accepted": {
        "uz": "✅ Buyurtma #{order_id} siz tomoningizdan qabul qilindi.",
        "ru": "✅ Заказ #{order_id} принят вами.",
        "en": "✅ Order #{order_id} accepted by you.",
    },
    "order_rejected": {
        "uz": "❌ Buyurtma #{order_id} rad etildi.",
        "ru": "❌ Заказ #{order_id} отклонён.",
        "en": "❌ Order #{order_id} rejected.",
    },
    "order_already_accepted": {
        "uz": "ℹ️ Buyurtma #{order_id} allaqachon qabul qilingan.",
        "ru": "ℹ️ Заказ #{order_id} уже принят.",
        "en": "ℹ️ Order #{order_id} already accepted.",
    },
    "order_status_updated": {
        "uz": "📦 Buyurtma #{order_id} holati: {status}",
        "ru": "📦 Статус заказа #{order_id}: {status}",
        "en": "📦 Order #{order_id} status: {status}",
    },

    # ========== STATISTIKA MATNLARI ==========
    "statistic_title": {
        "uz": "📊 Statistika ({period})",
        "ru": "📊 Статистика ({period})",
        "en": "📊 Statistics ({period})",
    },
    "statistic_body": {
        "uz": (
            "🏪 Do'konlar soni: {markets_count}\n"
            "👷 Ishchilar soni: {staff_count}\n\n"
            "📦 Sotilgan mahsulotlar soni: {sold_qty}\n"
            "🚚 Yetkazib berilgan: {delivered_qty}\n"
            "🚶 Olib ketilgan: {pickup_qty}\n"
            "💰 Sotuvdan tushgan summa: {sold_sum}\n\n"
            "📦 Omborda qolgan mahsulotlar soni: {stock_qty}\n"
            "💰 Ombordagi mahsulotlar summasi: {stock_sum}"
        ),
        "ru": (
            "🏪 Магазинов: {markets_count}\n"
            "👷 Сотрудников: {staff_count}\n\n"
            "📦 Продано товаров: {sold_qty}\n"
            "🚚 Доставлено: {delivered_qty}\n"
            "🚶 Забрали сами: {pickup_qty}\n"
            "💰 Сумма продаж: {sold_sum}\n\n"
            "📦 Осталось на складе: {stock_qty}\n"
            "💰 Сумма остатков: {stock_sum}"
        ),
        "en": (
            "🏪 Markets: {markets_count}\n"
            "👷 Staff: {staff_count}\n\n"
            "📦 Products sold: {sold_qty}\n"
            "🚚 Delivered: {delivered_qty}\n"
            "🚶 Picked up: {pickup_qty}\n"
            "💰 Sales total: {sold_sum}\n\n"
            "📦 In stock: {stock_qty}\n"
            "💰 Stock value: {stock_sum}"
        ),
    },
    "statistic_period_today": {"uz": "Bugun", "ru": "Сегодня", "en": "Today"},
    "statistic_period_week": {"uz": "Hafta", "ru": "Неделя", "en": "Week"},
    "statistic_period_month": {"uz": "Oy", "ru": "Месяц", "en": "Month"},
    "statistic_period_year": {"uz": "Yil", "ru": "Год", "en": "Year"},
    "invalid_period": {
        "uz": "❌ Sana formati noto'g'ri. Masalan: 11.08.2026 yoki 08.2026 yoki 2026",
        "ru": "❌ Неверный формат даты. Например: 11.08.2026 или 08.2026 или 2026",
        "en": "❌ Invalid date format. Example: 11.08.2026 or 08.2026 or 2026",
    },
    "statistic_custom_period_hint": {
        "uz": "\n\nYoki maxsus davrni yozib kiriting:\nkun.oy.yil (11.08.2026), oy.yil (08.2026) yoki yil (2026)",
        "ru": "\n\nИли введите свой период:\nдень.месяц.год (11.08.2026), месяц.год (08.2026) или год (2026)",
        "en": "\n\nOr type a custom period:\nday.month.year (11.08.2026), month.year (08.2026), or year (2026)",
    },

    # ========== XATOLIK MATNLARI ==========
    "error_occurred": {
        "uz": "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
        "ru": "❌ Произошла ошибка. Пожалуйста, попробуйте снова.",
        "en": "❌ An error occurred. Please try again.",
    },
    "access_denied": {
        "uz": "⛔ Bu amalni bajarish uchun ruxsat yo'q!",
        "ru": "⛔ Нет прав для выполнения этого действия!",
        "en": "⛔ Access denied!",
    },
    "invalid_input": {
        "uz": "❌ Noto'g'ri ma'lumot kiritildi. Iltimos, qaytadan urinib ko'ring.",
        "ru": "❌ Введены неверные данные. Пожалуйста, попробуйте снова.",
        "en": "❌ Invalid input. Please try again.",
    },
    "only_numbers": {
        "uz": "❌ Iltimos, faqat raqam kiriting!",
        "ru": "❌ Пожалуйста, введите только число!",
        "en": "❌ Please enter only numbers!",
    },

    # ========== KONFIRMASYON MATNLARI ==========
    "confirm_delete_market": {
        "uz": "⚠️ '{name}' do'konini o'chirishni tasdiqlaysizmi?",
        "ru": "⚠️ Подтверждаете удаление магазина '{name}'?",
        "en": "⚠️ Confirm delete market '{name}'?",
    },
    "confirm_delete_product": {
        "uz": "⚠️ '{name}' mahsulotini o'chirishni tasdiqlaysizmi?",
        "ru": "⚠️ Подтверждаете удаление товара '{name}'?",
        "en": "⚠️ Confirm delete product '{name}'?",
    },
    "confirm_btn": {
        "uz": "✅ Ha, tasdiqlayman",
        "ru": "✅ Да, подтверждаю",
        "en": "✅ Yes, confirm",
    },
    "cancel_btn": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Отмена",
        "en": "❌ Cancel",
    },
    "canceled": {
        "uz": "❌ Bekor qilindi.",
        "ru": "❌ Отменено.",
        "en": "❌ Canceled.",
    },
    "empty_list": {
        "uz": "Ro'yxat bo'sh.",
        "ru": "Список пуст.",
        "en": "List is empty.",
    },
}


def get_employe_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Admin/ishchi tarjimalarini olish uchun funksiya"""
    entry = LEXICON_EMPLOYE.get(key, {})
    template = entry.get(lang) or entry.get("uz") or key
    return template.format(**kwargs) if kwargs else template


# Telegramning "Menu" ro'yxatida ADMIN uchun ko'rinadigan komandalar.
LEXICON_COMMANDS_ADMIN: dict[str, list[tuple[str, str]]] = {
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

LEXICON_COMMANDS_STAFF: dict[str, list[tuple[str, str]]] = {
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
