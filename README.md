# 🌳 Qizil Tut | Baraka — Telegram Market Bot

**Texnologiyalar:** aiogram 3.x · SQLAlchemy 2.0 (async, class-based modellar) · PostgreSQL (psycopg3) · Redis · Docker Compose

Ko'p do'konli onlayn-savdo boti. Ko'p tillik (🇺🇿 o'zbek, 🇷🇺 rus, 🇬🇧 ingliz), uch xil rol: **Xaridor**, **Admin** (do'kon darajasida yoki super-admin), **Ishchi** (hozircha uzib qo'yilgan — pastga qarang).

## Loyiha tuzilishi

```
qizil_tut_market_bot/
├── bot/
│   ├── config.py                 # .env sozlamalari
│   ├── enums/enum.py             # UserRole, Language, OrderStatus, DeliveryType
│   ├── models/                   # SQLAlchemy class-based modellar
│   │   ├── abstract_models.py    # BaseModels (create_data/update_data)
│   │   ├── user_model.py         # UserModel, Address
│   │   ├── market_model.py       # MarketModel (billz_shop_id, billz_secret_key — shifrlangan)
│   │   ├── category_model.py     # CategoryModel
│   │   ├── brand_model.py        # BrandModel (mahsulot brendi, ixtiyoriy)
│   │   ├── product_model.py      # ProductsModel
│   │   ├── order_model.py        # OrderModel, OrderItemModel
│   │   ├── statistic_model.py    # StatisticModel (har bir sotuv uchun log)
│   │   └── feedback_model.py     # FeedbackModel (foydalanuvchi fikrlari)
│   ├── database/
│   │   ├── engine.py             # async engine/session, init_db()
│   │   └── repository/           # CRUD funksiyalar (domen bo'yicha bo'lingan)
│   ├── services/billz_sync.py    # Billz.io bilan davriy mahsulot sinxronizatsiyasi
│   ├── redis/redis_client.py     # Savat (cart) — Redis hash
│   ├── lexicons/                 # uz/ru/en tarjimalar (dictionary-based)
│   ├── states/states.py          # FSM holatlari
│   ├── keyboards/                # Inline/Reply klaviaturalar
│   ├── filters/role_filters.py   # IsAdmin, IsSuperAdmin, IsStaff
│   ├── middlewares/
│   │   ├── database.py           # har update uchun DB session
│   │   └── user_context.py       # db_user, lang, ban tekshiruvi
│   ├── utils/
│   │   ├── args.py               # qo'shtirnoqli argumentlarni ajratish
│   │   ├── commands.py           # rolga qarab bot komandalarini sozlash
│   │   ├── period.py             # statistika sana formatlarini tahlil qilish
│   │   └── crypto.py             # Billz kalitini shifrlash/deshifrlash (Fernet)
│   ├── assets/logo.jpg           # /start'da ko'rsatiladigan logotip
│   └── handlers/
│       ├── common/               # /start, til tanlash, ro'yxatdan o'tish, /help
│       ├── user/                 # xarid, savat, checkout, profil, sozlamalar, fikr
│       ├── admin/                # mahsulot/kategoriya/brend/do'kon/ban/statistika/buyurtmalar ro'yxati
│       └── staff/orders.py       # buyurtma qabul/rad qilish (IsAdmin — admin/super-admin uchun ishlaydi)
├── sql/add_billz_integration.sql   # mavjud bazaga Billz ustunlarini qo'shish uchun
├── scripts/
│   ├── backup_db.sh               # kunlik pg_dump zaxira (+ ixtiyoriy DO Spaces yuklash)
│   └── restore_db.sh              # zaxiradan tiklash
├── main.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Texnologiyalar nima uchun ishlatilgan

- **PostgreSQL + SQLAlchemy (async, psycopg3)** — barcha doimiy ma'lumotlar: foydalanuvchilar, do'konlar, kategoriyalar, brendlar, mahsulotlar, buyurtmalar, statistika, fikrlar.
- **Redis** — foydalanuvchi savati (`cart:{user_id}` hash) va aiogram FSM Storage (bot qayta ishga tushsa ham checkout/registratsiya jarayoni yo'qolmasligi uchun). Parol bilan himoyalangan (`REDIS_PASSWORD`).
- **aiogram 3.x** — Router, Filter (F), FSM, middleware asosida modulli arxitektura.
- **Docker Compose** — PostgreSQL va Redis'ni bir buyruq bilan ko'tarish uchun (portlar faqat `127.0.0.1`ga bog'langan — tashqi internetga ochiq emas).
- **cryptography (Fernet)** — Billz.io API kalitini bazada shifrlangan holda saqlash uchun.

## O'rnatish

```bash
cd qizil_tut_market_bot
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env faylni oching va to'ldiring:
#  - BOT_TOKEN            — @BotFather'dan (MAJBURIY, bo'lmasa bot ishga tushmaydi)
#  - SUPER_ADMIN_IDS      — botni birinchi /start qilganda avtomatik SUPER_ADMIN bo'ladigan ID'lar
#  - POSTGRES_PASSWORD    — kuchli parol qo'ying (standart qiymatni qoldirmang)
#  - REDIS_PASSWORD       — Redis uchun parol (docker-compose --requirepass shu qiymatni ishlatadi)
#  - ENCRYPTION_KEY       — Billz kalitlarini shifrlash uchun: `python -m bot.utils.crypto`
#                           bilan generatsiya qiling. YO'QOTMANG — yo'qolsa, saqlangan
#                           Billz kalitlarini qayta tiklab bo'lmaydi.

docker compose --env-file .env up -d   # Postgres + Redis

python main.py
```

Birinchi ishga tushganda jadvallar avtomatik yaratiladi (`init_db()` → `create_all()`). Agar loyihani **allaqachon ishlab turgan** bazaga o'rnatayotgan bo'lsangiz (masalan Billz integratsiyasi qo'shilgandan keyin), `create_all()` yangi jadval qo'shadi, lekin mavjud jadvalga yangi ustun qo'shib bermaydi — bunday holatda `sql/add_billz_integration.sql` skriptini bir marta qo'lda ishga tushiring:

```bash
docker exec -i <postgres_container> psql -U <user> -d <database> < sql/add_billz_integration.sql
```

Skript idempotent (bir necha marta ishga tushirsangiz ham xavfsiz). Production uchun Alembic migratsiyalariga o'tish tavsiya etiladi (`requirements.txt`da bor, lekin hali sozlanmagan).

### Zaxira nusxalash (backup)

```bash
bash scripts/backup_db.sh
```

Kunlik avtomatik ishga tushirish uchun cron'ga qo'shing (`scripts/backup_db.sh` faylining boshida namuna bor). Zaxira `backups/` papkasiga saqlanadi, 7 kundan eskisi avtomatik o'chiriladi. Ixtiyoriy ravishda `.env`da `SPACES_BUCKET` va boshqa `SPACES_*` qiymatlarni to'ldirsangiz, zaxira DigitalOcean Spaces'ga ham nusxalanadi. Tiklash uchun: `bash scripts/restore_db.sh <fayl>`.

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

**SUPER_ADMIN** asosiy paneli:

- **👥 Admin boshqaruvi** / **🏪 Do'kon boshqaruvi** — faqat SUPER_ADMIN
- **🚫 Ban/Unban** — foydalanuvchini bloklash/blokdan chiqarish
- **📦 Mahsulotlar bo'limi** — submenyu, ichida:
  - **📦 Mahsulot boshqaruvi** — qo'shish (brend → kategoriya → rasm ketma-ketligida, tugma orqali tanlab yoki "+ Yangi" bilan joyida qo'shib), tahrirlash, o'chirish, ro'yxat
  - **🗂 Kategoriyalar** / **🏷 Brendlar** — qo'shish, o'chirish, ro'yxat (mahsulotli kategoriyani o'chirish bloklanadi)
- **📊 Statistika** — tayyor davrlar (bugun/hafta/oy/yil) yoki qo'lda kiritilgan sana oralig'i bo'yicha savdo hisoboti
- **💬 Fikrlar** — foydalanuvchilar qoldirgan fikrlarni birma-bir ko'rish va "ko'rib chiqildi" deb belgilash
- **📦 Buyurtmalar** — barcha do'konlar buyurtmalari, status bo'yicha filtrlangan ro'yxat

**ADMIN** (do'kon boshqaruvchisi) paneli — faqat o'z do'koniga tegishli: 📦 Mahsulot boshqaruvi, 🚫 Ban, 📊 Statistika, 💬 Fikrlar, 📦 Buyurtmalar (kategoriya/brend/do'kon/admin boshqaruvi ko'rinmaydi).

`/help` — SUPER_ADMIN, ADMIN, STAFF va oddiy foydalanuvchi uchun **rolga mos alohida matn** chiqaradi (`bot/lexicons/lexicon_text.py`: `help_admin`, `help_market_admin`, `help_user`).

## Buyurtmalarni ko'rish va qabul/rad qilish

Ikkita joydan boshqariladi:

1. **Yangi buyurtma bildirishnomasi** — buyurtma tushganda avtomatik yuboriladi, ✅/❌ tugmalari bilan.
2. **📦 Buyurtmalar** bo'limi (`bot/handlers/admin/orders_list.py`) — status bo'yicha (yangi/tasdiqlangan/bekor qilingan) sahifalab ko'rish; **YANGI** holatdagi buyurtma tafsilotida ham xuddi shu ✅ Qabul qilish / ❌ Rad etish tugmalari chiqadi.

Ikkalasi ham `bot/handlers/staff/orders.py`dagi bitta umumiy mexanizmni ishlatadi (`IsAdmin` filtri — nomiga qaramay endi ADMIN/SUPER_ADMIN uchun ishlaydi). ADMIN (do'kon boshqaruvchisi) faqat **o'z do'koniga tegishli** buyurtmalarni ko'radi va boshqaradi — boshqa do'konning buyurtmasiga ruxsati yo'q. Qabul qilinganda buyurtma holati o'zgaradi; rad etilganda esa **ombordagi son qaytariladi** va statistika yozuvi o'chiriladi (chunki sotuv haqiqatda amalga oshmagan).

## Billz.io integratsiyasi (POS sinxronizatsiyasi)

`BILLZ_SYNC_ENABLED=true` bo'lsa, har `BILLZ_SYNC_INTERVAL_MINUTES` daqiqada Billz'ga bog'langan har bir do'kon o'zining API kaliti bilan so'raladi va mahsulotlar (nom/narx/son/rasm) avtomatik yangilanadi (`bot/services/billz_sync.py`). Do'konni bog'lash: **Do'kon boshqaruvi → 🔗 Billz bilan bog'lash** (faqat SUPER_ADMIN). Billz bilan bog'langan do'konning mahsulotlari admin panelda qo'lda tahrirlanmaydi — faqat Billz orqali boshqariladi.

Har bir do'kon Billz'da o'zining alohida akkauntiga (alohida API kalitiga) ega — kalit `MarketModel.billz_secret_key`da, bazada **shifrlangan** holda saqlanadi (pastga qarang).

## Xavfsizlik

- **Billz API kaliti shifrlangan** — `bot/utils/crypto.py` (Fernet), master kalit `.env`dagi `ENCRYPTION_KEY`. Bazaga to'g'ridan-to'g'ri kirilsa ham (masalan backup fayl orqali), kalit ochiq matnda ko'rinmaydi.
- **Redis parol bilan himoyalangan** (`REDIS_PASSWORD`, `docker-compose.yml`dagi `--requirepass`).
- **Postgres/Redis portlari faqat `127.0.0.1`ga bog'langan** — tashqi internetdan to'g'ridan-to'g'ri ulanib bo'lmaydi.
- Do'kon admin(i) faqat **o'z do'koniga** tegishli mahsulot/buyurtma/statistikani ko'ra va boshqara oladi — barcha shunday handlerlarda egalik tekshiruvi bor (`ap_market_pick`, `_belongs_to_admin` va h.k.).

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
5. **`ENCRYPTION_KEY` yo'qolsa**, bazadagi shifrlangan Billz kalitlarini hech qanday tarzda qayta tiklab bo'lmaydi — har bir do'kon uchun kalitni qaytadan kiritishga to'g'ri keladi. Bu qiymatni `.env`dan tashqarida (masalan alohida secrets manager yoki xavfsiz backup) ham saqlab qo'yish tavsiya etiladi.