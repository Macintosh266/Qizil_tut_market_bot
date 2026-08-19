# 🛍 Online Market Telegram Bot

**Texnologiyalar:** aiogram 3.x · SQLAlchemy 2.0 (async, class-based modellar) · PostgreSQL (psycopg3) · Redis · Docker Compose

Ko'p tillik (🇺🇿 o'zbek, 🇷🇺 rus, 🇬🇧 ingliz), uch xil panel: **Xaridor**, **Ishchi**, **Admin**.

## Loyiha tuzilishi

```
online_market_bot/
├── bot/
│   ├── config.py               # .env sozlamalari
│   ├── enums/enum.py           # UserRole, Language, OrderStatus, DeliveryType
│   ├── models/                 # SQLAlchemy class-based modellar
│   │   ├── abstract_models.py  # BaseModels (create_data/update_data)
│   │   ├── user_model.py       # UserModel, Address
│   │   ├── market_model.py     # MarketModel
│   │   ├── category_model.py   # CategoryModel (self-referential)
│   │   ├── product_model.py    # ProductsModel
│   │   ├── order_model.py      # OrderModel, OrderItemModel
│   │   └── statistic_model.py  # StatisticModel (har bir sotuv uchun log)
│   ├── database/
│   │   ├── engine.py           # async engine/session, init_db()
│   │   └── repository/         # CRUD funksiyalar (domen bo'yicha bo'lingan)
│   ├── redis/redis_client.py   # Savat (cart) — Redis hash
│   ├── i18n/                   # uz/ru/en tarjimalar (dictionary-based)
│   ├── states/states.py        # FSM holatlari
│   ├── keyboards/               # Inline/Reply klaviaturalar
│   ├── filters/role_filters.py # IsAdmin, IsStaff
│   ├── middlewares/
│   │   ├── database.py         # har update uchun DB session
│   │   └── user_context.py     # db_user, lang, ban tekshiruvi
│   ├── utils/
│   │   ├── args.py             # qo'shtirnoqli argumentlarni ajratish
│   │   └── period.py           # /statistic sana formatlarini tahlil qilish
│   └── handlers/
│       ├── common/start.py     # /start, til tanlash, ro'yxatdan o'tish, /help
│       ├── user/               # xarid, savat, checkout, profil, sozlamalar
│       ├── admin/              # barcha admin buyruqlari
│       └── staff/orders.py     # buyurtmani qabul qilish
├── main.py
├── requirements.txt
├── docker-compose.yml
└── .env.example
```

## Texnologiyalar nima uchun ishlatilgan

- **PostgreSQL + SQLAlchemy (async, psycopg3)** — barcha doimiy ma'lumotlar: foydalanuvchilar, do'konlar, kategoriyalar, mahsulotlar, buyurtmalar, statistika.
- **Redis** — foydalanuvchi savati (`cart:{user_id}` hash, tez-tez o'zgaradigan vaqtinchalik ma'lumot) va aiogram FSM Storage (bot qayta ishga tushsa ham checkout/registratsiya jarayoni yo'qolmasligi uchun).
- **aiogram 3.x** — Router, Filter (F), FSM, middleware asosida modulli arxitektura.
- **Docker Compose** — PostgreSQL va Redis'ni bir buyruq bilan ko'tarish uchun.

## O'rnatish

```bash
cd online_market_bot
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env faylni oching: BOT_TOKEN va SUPER_ADMIN_IDS ni to'ldiring
# (SUPER_ADMIN_IDS - botni birinchi /start qilganda avtomatik ADMIN bo'ladigan ID'lar)

docker compose --env-file .env up -d   # Postgres + Redis

python main.py
```

Birinchi ishga tushganda jadvallar avtomatik yaratiladi (`init_db()`). Production uchun Alembic migratsiyalariga o'tish tavsiya etiladi.

## Buyruqlar

**Hammaga:**
- `/start` — ro'yxatdan o'tish / botni boshlash
- `/help` — yordam (rolga qarab moslashadi)

**Faqat Admin** (`.env` dagi `SUPER_ADMIN_IDS` yoki `/add_admin` orqali tayinlanganlar):
```
/add_admin <user_id yoki username>
/delete_admin <user_id yoki username>
/add_staff <user_id yoki username>
/delete_staff <user_id yoki username>
/ban <user_id yoki username>
/unban <user_id yoki username>
/add_market "Do'kon nomi" "Do'kon manzili"
/delete_market "Do'kon nomi"
/add_product "Do'kon nomi" "Mahsulot nomi" <soni> <narhi> ["Kategoriya"]
/delete_product "Do'kon nomi" "Mahsulot nomi"
/statistic <kun.oy.yil | oy.yil | yil>     masalan: /statistic 11.08.2026
```

> Ko'p so'zli nomlar (do'kon/mahsulot) qo'shtirnoq ichida yozilishi kerak — buyruq argumentlari `shlex` orqali ajratiladi (`bot/utils/args.py`).

**Xaridor menyusi (tugmalar orqali):**
- 🛍 Xarid qilish → do'kon → kategoriya (yoki qidiruv) → mahsulot → miqdor → savat
- 🛒 Savat → miqdorni ➕/➖ o'zgartirish, ❌ o'chirish, buyurtma qilish (🚶 o'zi olib ketish / 🚚 yetkazib berish)
- 👤 Profil — ID, ism, username, til, telefon, manzil
- ⚙️ Sozlamalar — til, manzil, ism o'zgartirish

**Ishchi:** yangi buyurtma tushganda xabar keladi (hozircha `SUPER_ADMIN_IDS`ga yuboriladi — pastdagi eslatmaga qarang), "✅ Qabul qilish" tugmasi bilan buyurtmani o'ziga biriktiradi.

## Statistic modeli — muhim arxitektura qarori

`StatisticModel` — bu **oldindan hisoblangan yig'indi emas**, balki **har bir sotilgan mahsulot uchun alohida log yozuvi**. Sabab: `/statistic` istalgan davr (kun/oy/yil) uchun ishlashi kerak; log jadvali bo'lsa, istalgan davr uchun oddiy `SUM()/GROUP BY` bilan javob olinadi — oldindan hisoblab qo'yilgan raqamni har safar qayta hisoblash shart bo'lmaydi.

Yozuv **buyurtma checkout qilinganda** (`create_order_with_statistics`) yaratiladi va shu paytda mahsulot ombordagi soni ham kamayadi.

## Bilib qo'yish kerak bo'lgan soddalashtirishlar (keyingi qadamlar)

Loyiha hajmi katta bo'lgani uchun quyidagilar **soddalashtirilgan holda** ishlaydi — production'ga chiqarishdan oldin kengaytirish tavsiya etiladi:

1. **Yangi buyurtma xabarnomasi** hozircha faqat `.env`dagi `SUPER_ADMIN_IDS`ga yuboriladi. To'g'ri yechim: bazadagi barcha `STAFF`/`ADMIN` rolidagi foydalanuvchilarga yuborish (`get_user_by_id_or_username` kabi yangi repository funksiyasi kerak).
2. **Statistika do'kon kesimida emas, umumiy** hisoblanadi (`get_period_statistics`). Kerak bo'lsa `market_id` bo'yicha filtr qo'shish oson (`statistic_repo.py`ga parametr qo'shiladi).
3. **Ombordagi mahsulot yetarliligi** faqat savatga qo'shishda tekshiriladi, checkout paytida qayta tekshirilmaydi — bir vaqtning o'zida bir nechta xaridor bir xil mahsulotni sotib olsa, nazariy jihatdan "manfiy stock" yuzaga kelishi mumkin (kam ehtimol, lekin production'da `SELECT ... FOR UPDATE` yoki optimistik lock qo'shish tavsiya etiladi).
4. **Alembic** hozircha ulanmagan — `init_db()` faqat `create_all()` qiladi. Sxema o'zgarganda avtomatik migratsiya yo'q.
5. **Kategoriya-do'kon bog'lanishi** faqat mahsulot orqali ("shu do'konda shu kategoriyada mahsulot bormi") — agar bo'sh kategoriyalarni ham do'konga ochiq-oydin biriktirish kerak bo'lsa, `CategoryModel`ga `market_id` qo'shish kerak bo'ladi.
