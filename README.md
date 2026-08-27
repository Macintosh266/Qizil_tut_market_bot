# 🌳 Qizil Tut | Baraka — Telegram Market Bot

**Texnologiyalar:** aiogram 3.x · SQLAlchemy 2.0 (async, class-based modellar) · PostgreSQL (psycopg3) · Redis · Docker Compose

Ko'p do'konli onlayn-savdo boti. Ko'p tillik (🇺🇿 o'zbek, 🇷🇺 rus, 🇬🇧 ingliz), uch xil rol: **Xaridor**, **Admin** (do'kon darajasida yoki super-admin), **Ishchi** (hozircha uzib qo'yilgan — pastga qarang).

## Loyiha tuzilishi

qizil_tut_market_bot/
├── bot/
│ ├── config.py # .env sozlamalari
│ ├── enums/enum.py # UserRole, Language, OrderStatus, DeliveryType
│ ├── models/ # SQLAlchemy class-based modellar
│ │ ├── abstract_models.py # BaseModels (create_data/update_data)
│ │ ├── user_model.py # UserModel, Address
│ │ ├── market_model.py # MarketModel
│ │ ├── category_model.py # CategoryModel
│ │ ├── brand_model.py # BrandModel (mahsulot brendi, ixtiyoriy)
│ │ ├── product_model.py # ProductsModel
│ │ ├── order_model.py # OrderModel, OrderItemModel
│ │ ├── statistic_model.py # StatisticModel (har bir sotuv uchun log)
│ │ └── feedback_model.py # FeedbackModel (foydalanuvchi fikrlari)
│ ├── database/
│ │ ├── engine.py # async engine/session, init_db()
│ │ └── repository/ # CRUD funksiyalar (domen bo'yicha bo'lingan)
│ ├── redis/redis_client.py # Savat (cart) — Redis hash
│ ├── lexicons/ # uz/ru/en tarjimalar (dictionary-based)
│ ├── states/states.py # FSM holatlari
│ ├── keyboards/ # Inline/Reply klaviaturalar
│ ├── filters/role_filters.py # IsAdmin, IsSuperAdmin, IsStaff
│ ├── middlewares/
│ │ ├── database.py # har update uchun DB session
│ │ └── user_context.py # db_user, lang, ban tekshiruvi
│ ├── utils/
│ │ ├── args.py # qo'shtirnoqli argumentlarni ajratish
│ │ ├── commands.py # rolga qarab bot komandalarini sozlash
│ │ └── period.py # statistika sana formatlarini tahlil qilish
│ ├── assets/logo.jpg # /start'da ko'rsatiladigan logotip
│ └── handlers/
│ ├── common/ # /start, til tanlash, ro'yxatdan o'tish, /help
│ ├── user/ # xarid, savat, checkout, profil, sozlamalar, fikr
│ ├── admin/ # mahsulot/kategoriya/brend/do'kon/ban/statistika/buyurtma
│ └── staff/orders.py # buyurtma qabul qilish (hozircha ulanmagan)
├── sql/add_brand_and_feedback.sql # mavjud bazaga qo'shimcha ustun/jadval qo'shish uchun
├── main.py
├── requirements.txt
├── docker-compose.yml
└── .env.example


## Texnologiyalar nima uchun ishlatilgan

- **PostgreSQL + SQLAlchemy (async, psycopg3)** — barcha doimiy ma'lumotlar: foydalanuvchilar, do'konlar, kategoriyalar, brendlar, mahsulotlar, buyurtmalar, statistika, fikrlar.
- **Redis** — foydalanuvchi savati (`cart:{user_id}` hash) va aiogram FSM Storage (bot qayta ishga tushsa ham checkout/registratsiya jarayoni yo'qolmasligi uchun).
- **aiogram 3.x** — Router, Filter (F), FSM, middleware asosida modulli arxitektura.
- **Docker Compose** — PostgreSQL va Redis'ni bir buyruq bilan ko'tarish uchun.

## O'rnatish

```bash
cd qizil_tut_market_bot
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env faylni oching: BOT_TOKEN va SUPER_ADMIN_IDS ni to'ldiring
# (SUPER_ADMIN_IDS — botni birinchi /start qilganda avtomatik SUPER_ADMIN bo'ladigan ID'lar)

docker compose --env-file .env up -d   # Postgres + Redis

python main.py
```

Birinchi ishga tushganda jadvallar avtomatik yaratiladi (`init_db()` → `create_all()`). Agar loyihani **allaqachon ishlab turgan** bazaga o'rnatayotgan bo'lsangiz (masalan brend/fikr funksiyasi qo'shilgandan keyin), `create_all()` yangi jadval qo'shadi, lekin mavjud jadvalga yangi ustun qo'shib bermaydi — bunday holatda `sql/add_brand_and_feedback.sql` skriptini bir marta qo'lda ishga tushiring:

```bash
docker exec -i <postgres_container> psql -U <user> -d <database> < sql/add_brand_and_feedback.sql
```

Skript idempotent (bir necha marta ishga tushirsangiz ham xavfsiz). Production uchun Alembic migratsiyalariga o'tish tavsiya etiladi (`requirements.txt`da bor, lekin hali sozlanmagan).

## Rollar

| Rol | Huquqi |
|---|---|
| **USER** | oddiy xaridor |
| **ADMIN** | bitta do'konga bog'langan — o'sha do'kon mahsulotlari, statistikasi, ban |
| **SUPER_ADMIN** | barcha do'konlar + admin/do'kon/kategoriya/brend boshqaruvi |
| **STAFF** | hozircha **uzib qo'yilgan** (kod saqlangan, router ulanmagan) — pastga qarang |

## Xaridor oqimi

1. **🛍 Xarid qilish** → do'konni tanlash
2. Do'kon tanlangach — **brendlar** qatori, **kategoriyalar** qatori va **mahsulotlar ro'yxati** (nomi — narxi tugmalari) ketma-ket chiqadi
   - Ro'yxat rasmsiz, tugma ko'rinishida; 10 tadan ko'p mahsulot bo'lsa `◀️ 1/2 ▶️` sahifalash paydo bo'ladi — sahifa almashtirilganda xabar qayta yuborilmaydi, mavjudi tahrirlanadi
   - Kategoriya yoki brend tugmasi bosilsa, xuddi shu ro'yxat filtrlangan holda yangilanadi
   - Yozib qidirish ham ishlaydi (ro'yxat o'rniga so'rov natijalari chiqadi)
3. Mahsulot tanlansa — **rasm + tavsif + narx + omborda soni**, hamda 🛒 savatga qo'shish va miqdorni ➕/➖ yoki tugmani bosib qo'lda kiritish imkoniyati bilan ochiladi
4. **🛒 Savat** → miqdorni o'zgartirish/o'chirish, **✅ Buyurtma qilish**
5. Yetkazib berish turi: 🚶 o'zi olib ketish yoki 🚚 yetkazib berish (manzil — matn yoki xaritadan lokatsiya)
6. Buyurtma tasdiqlangach, **super-adminlarga** mahsulotlar ro'yxati, rasmlari va yetkazib berish ma'lumoti (manzil/lokatsiya) bilan bildirishnoma boradi, ular ✅ **Qabul qilish** / ❌ **Rad etish** tugmalari orqali javob beradi
7. Admin javobidan so'ng **mijozga ham xabar** boradi ("qabul qilindi" / "rad etildi")
8. **💬 Fikr bildirish** — istalgan vaqtda matn yozib fikr/taklif/shikoyat qoldirish mumkin

## Admin panel (reply-klaviatura bo'limlari)

- **📦 Mahsulotlar** — qo'shish (brend → kategoriya → rasm ketma-ketligida, tugma orqali tanlab yoki "+ Yangi" bilan joyida qo'shib), tahrirlash, o'chirish, ro'yxat
- **🗂 Kategoriyalar** / **🏷 Brendlar** — qo'shish, o'chirish, ro'yxat (faqat SUPER_ADMIN; mahsulotli kategoriyani o'chirish bloklanadi)
- **🏪 Do'konlar** / **👤 Adminlar** — faqat SUPER_ADMIN
- **🚫 Ban** — foydalanuvchini bloklash/blokdan chiqarish
- **📊 Statistika** — tayyor davrlar (bugun/hafta/oy/yil) yoki qo'lda kiritilgan sana oralig'i bo'yicha savdo hisoboti
- **💬 Fikrlar** — foydalanuvchilar qoldirgan fikrlarni birma-bir ko'rish va "ko'rib chiqildi" deb belgilash

## Buyurtmani qabul/rad qilish

Yangi buyurtma bildirishnomasidagi tugmalarni **admin va super-admin** bosishi mumkin (`bot/handlers/staff/orders.py`, `IsAdmin` filtri bilan — nomiga qaramay, endi staff emas, admin uchun ishlaydi). Qabul qilinganda buyurtma holati o'zgaradi; rad etilganda esa **ombordagi son qaytariladi** va statistika yozuvi o'chiriladi (chunki sotuv haqiqatda amalga oshmagan).

## STAFF funksiyasi haqida

STAFF roli va uning buyurtma-qabul-qilish paneli **kod darajasida to'liq saqlangan**, faqat quyidagi ikkita joyda router ulanishi izohga olingan:

- `bot/handlers/__init__.py` — `get_staff_router()` chaqiruvi
- `bot/handlers/admin/__init__.py` — "Xodimlar boshqaruvi" bo'limi

Qayta yoqish uchun shu ikki joydagi izohlarni ochish kifoya.

## `StatisticModel` — muhim arxitektura qarori

`StatisticModel` — bu **oldindan hisoblangan yig'indi emas**, balki **har bir sotilgan mahsulot uchun alohida log yozuvi**. Sabab: statistika istalgan davr (kun/oy/yil) uchun ishlashi kerak; log jadvali bo'lsa, istalgan davr uchun oddiy `SUM()/GROUP BY` bilan javob olinadi.

Yozuv buyurtma **tasdiqlanganda** (`create_order_with_statistics`) yaratiladi va shu paytda ombordagi son ham kamayadi — bu, boshqa xaridor xuddi shu mahsulotni sotib olib qo'ymasin uchun, mahsulotni "band qilib qo'yish" mantig'i. Agar admin keyin buyurtmani **rad etsa**, `reject_order()` bu ikkalasini (ombor va statistika) ortga qaytaradi.

## Bilib qo'yish kerak bo'lgan soddalashtirishlar

1. **Statistika do'kon kesimida emas, umumiy** hisoblanadi. Kerak bo'lsa `market_id` bo'yicha filtr qo'shish oson (`statistic_repo.py`).
2. **Ombordagi mahsulot yetarliligi** parallel so'rovlarda `SELECT ... FOR UPDATE` yoki optimistik lock bilan himoyalanmagan — nazariy jihatdan bir vaqtning o'zida ikki xaridor bir xil mahsulotni sotib olishga urinishi mumkin (kam ehtimol, lekin production'da e'tiborga olish tavsiya etiladi).
3. **Alembic** hali sozlanmagan — `init_db()` faqat `create_all()` qiladi, mavjud jadvalga ustun qo'shmaydi (shu sabab `sql/` papkasidagi qo'lda skript bor).
4. **Kategoriya-do'kon bog'lanishi** faqat mahsulot orqali aniqlanadi ("shu do'konda shu kategoriyada mahsulot bormi") — kategoriyaning o'zi global, do'konga qattiq bog'lanmagan.