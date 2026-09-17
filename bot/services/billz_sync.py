"""
Billz.io (POS/ombor tizimi) bilan mahsulotlarni IKKI TOMONLAMA sinxronlash.

MUHIM ARXITEKTURA QARORI: har bir do'kon (bot ichidagi MarketModel) Billz'da
o'zining ALOHIDA akkauntiga — demak, o'zining alohida API kalitiga ega.
Shuning uchun kalit botning umumiy .env sozlamasida emas, balki har bir
`MarketModel.billz_secret_key` ustunida saqlanadi.

MAHSULOTLAR — TO'LIQ AVTOMATIK, QO'LDA TAHRIRLASH YO'Q:
Do'kon Billz bilan bog'langan bo'lsa (`billz_secret_key` bor), o'sha
do'konning mahsulotlarini admin panelda QO'LDA qo'shib/tahrirlab/o'chirib
bo'lmaydi (`bot/handlers/admin/products.py`dagi tekshiruvga qarang) —
mahsulotlar FAQAT Billz orqali boshqariladi:
  - Billz'da mahsulot QO'SHILSA -> keyingi sinxronizatsiyada botda paydo bo'ladi
  - Billz'da mahsulot O'ZGARTIRILSA (narx/son/nom) -> botda ham yangilanadi
  - Billz'da mahsulot O'CHIRILSA -> botda ham deaktivatsiya qilinadi (is_active=False)

Ishlash printsipi: Billz'da webhook (push-xabarnoma) mexanizmi yo'q, shuning
uchun bu PULL (davriy so'rov) orqali ishlaydi — har N daqiqada
(`BILLZ_SYNC_INTERVAL_MINUTES`) har bir bog'langan do'kon o'zining kaliti
bilan so'raladi. Bu haqiqiy vaqtli emas (bir necha daqiqa kechikish
bo'ladi), lekin amalda yetarli.

DIQQAT — moslashtirish kerak bo'lgan joy:
Billz javobidagi aniq maydon nomlari (`item.name`, `item.price`,
`item.image_url` va h.k.) rasmiy `billzio-api` kutubxonasining ochiq
hujjatlashtirilgan namunasiga asoslangan ENG YAQIN TAXMIN. Birinchi ishga
tushirishda `_debug_dump_first_item()` bitta mahsulot obyektining BARCHA
haqiqiy maydonlarini logga chiqaradi — shuni ko'rib, kerak bo'lsa
`_map_product()` funksiyasidagi 2-3 qatorni to'g'irlang.
"""

import asyncio
import logging
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.repository.brand_repo import get_or_create_brand
from bot.database.repository.category_repo import get_or_create_category
from bot.database.repository.market_repo import get_market_billz_secret_key, get_markets_linked_to_billz
from bot.database.repository.product_repo import (
    deactivate_missing_billz_products,
    get_product_by_billz_id,
    upsert_product_from_billz,
)
from bot.models import MarketModel

logger = logging.getLogger(__name__)

_PAGE_SIZE = 100
_debug_dumped = False  # bitta ishga tushirishda faqat bir marta log chiqarish uchun

# Telegramning sendPhoto cheklovlari (~10MB, eni+bo'yi <=10000px) ga mos
# tushishi uchun rasmlarni shu o'lchamdan oshsa kichraytiramiz.
_MAX_IMAGE_DIMENSION = 1280
_MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _get_handler(secret_key: str):
    """`billzio-api` importi qasddan funksiya ichida — kutubxona
    o'rnatilmagan yoki versiyasi mos kelmasa, bu FAQAT Billz funksiyasi
    chaqirilganda xato beradi, butun bot ishga tushmay qolmaydi."""
    try:
        from billzio_api import AsyncBillzHandler
    except ImportError as exc:
        raise RuntimeError(
            "billzio-api kutubxonasi o'rnatilmagan. O'rnatish: pip install billzio-api"
        ) from exc

    return AsyncBillzHandler(secret_key)


async def verify_billz_key(secret_key: str) -> bool:
    """Do'konni bog'lash paytida kalitni sinab ko'rish uchun — bitta
    mahsulot so'rab, muvaffaqiyatli javob kelsa True qaytaradi."""
    try:
        from billzio_api import ProductsListFilters

        handler = _get_handler(secret_key)
        await handler.get_products(ProductsListFilters(limit=1, offset=0))
        return True
    except Exception:
        logger.exception("Billz kalitini tekshirishda xato")
        return False


def _map_product(item) -> dict:
    """Billz mahsulot obyektini bizning formatimizga o'giradi."""
    return {
        "billz_product_id": str(getattr(item, "id", None) or getattr(item, "product_id", None)),
        "name": getattr(item, "name", None) or getattr(item, "title", "Noma'lum mahsulot"),
        "price": float(getattr(item, "price", None) or getattr(item, "retail_price", 0) or 0),
        "stock": int(
            getattr(item, "count", None) or getattr(item, "quantity", None) or getattr(item, "remainder", 0) or 0
        ),
        "category_name": getattr(item, "category_name", None) or getattr(item, "category", None) or "Umumiy",
        "brand_name": getattr(item, "brand_name", None) or getattr(item, "brand", None),
        "description": getattr(item, "description", None),
        "image_url": (
            getattr(item, "image_url", None) or getattr(item, "photo_url", None) or getattr(item, "image", None)
        ),
    }


def _debug_dump_first_item(item) -> None:
    global _debug_dumped
    if _debug_dumped:
        return
    _debug_dumped = True
    try:
        raw = vars(item)
    except TypeError:
        raw = {"repr": repr(item)}
    logger.info("BILLZ DEBUG — birinchi mahsulot obyektining barcha maydonlari: %s", raw)


async def _fetch_and_store_image(bot, image_url: str) -> str | None:
    """
    Billz'dagi rasm URL'ini yuklab oladi, kerak bo'lsa (katta hajmda
    bo'lsa) Pillow bilan kichraytiradi, so'ng Telegram'ga bir marta
    yuklab, doimiy `file_id` oladi. Muvaffaqiyatsiz bo'lsa None qaytaradi.
    """
    try:
        import aiohttp
        from aiogram.types import BufferedInputFile
        from PIL import Image
    except ImportError:
        logger.warning("Pillow yoki aiohttp o'rnatilmagan — Billz rasmlari sinxronlanmaydi")
        return None

    try:
        async with aiohttp.ClientSession() as http:
            async with http.get(image_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return None
                raw = await resp.read()

        img = Image.open(BytesIO(raw))
        img = img.convert("RGB")

        if max(img.size) > _MAX_IMAGE_DIMENSION or len(raw) > _MAX_IMAGE_BYTES:
            img.thumbnail((_MAX_IMAGE_DIMENSION, _MAX_IMAGE_DIMENSION), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=85, optimize=True)
            raw = buf.getvalue()

        storage_chat_id = settings.BILLZ_IMAGE_STORAGE_CHAT_ID
        if not storage_chat_id:
            admin_ids = settings.super_admin_ids
            if not admin_ids:
                logger.warning("BILLZ_IMAGE_STORAGE_CHAT_ID va SUPER_ADMIN_IDS bo'sh — rasm yuklanmadi")
                return None
            storage_chat_id = admin_ids[0]

        sent = await bot.send_photo(
            storage_chat_id,
            BufferedInputFile(raw, filename="billz_product.jpg"),
            disable_notification=True,
        )
        return sent.photo[-1].file_id
    except Exception:
        logger.exception("Billz rasmini yuklashda xato: %s", image_url)
        return None


async def _sync_one_market(session: AsyncSession, market: MarketModel, bot=None) -> dict:
    """Bitta do'konni (o'zining Billz kaliti bilan) to'liq sinxronlaydi:
    yangi/o'zgargan mahsulotlarni yozadi, Billz'da endi yo'q mahsulotlarni
    deaktivatsiya qiladi."""
    from billzio_api import ProductsListFilters

    secret_key = get_market_billz_secret_key(market)
    if not secret_key:
        raise RuntimeError(
            "Billz kalitini deshifrlab bo'lmadi (ENCRYPTION_KEY noto'g'ri yoki o'zgargan) — "
            "do'konni qaytadan bog'lash kerak bo'lishi mumkin"
        )

    handler = _get_handler(secret_key)
    seen_billz_ids: set[str] = set()
    result = {"created": 0, "updated": 0}

    offset = 0
    while True:
        page = await handler.get_products(ProductsListFilters(limit=_PAGE_SIZE, offset=offset))
        items = getattr(page, "products", None) or getattr(page, "items", [])
        if not items:
            break

        for item in items:
            _debug_dump_first_item(item)
            data = _map_product(item)
            if not data["billz_product_id"] or data["billz_product_id"] == "None":
                continue

            seen_billz_ids.add(data["billz_product_id"])

            category = await get_or_create_category(session, data["category_name"])
            brand = None
            if data["brand_name"]:
                brand = await get_or_create_brand(session, data["brand_name"])

            # Rasmni faqat mahsulotda hali rasm yo'q bo'lsa yuklaymiz —
            # har safar qayta yuklab, ortiqcha trafik sarflamaslik uchun.
            image_file_id = None
            if bot is not None and data["image_url"]:
                existing = await get_product_by_billz_id(session, data["billz_product_id"])
                if not existing or not existing.image_file_id:
                    image_file_id = await _fetch_and_store_image(bot, data["image_url"])

            _, created = await upsert_product_from_billz(
                session,
                billz_product_id=data["billz_product_id"],
                market_id=market.id,
                category_id=category.id,
                brand_id=brand.id if brand else None,
                name=data["name"],
                price=data["price"],
                stock=data["stock"],
                description=data["description"],
                image_file_id=image_file_id,
            )
            result["created" if created else "updated"] += 1

        if len(items) < _PAGE_SIZE:
            break
        offset += _PAGE_SIZE

    # Billz'da endi yo'q (o'chirilgan) mahsulotlarni botda ham deaktivatsiya qilamiz
    result["deactivated"] = await deactivate_missing_billz_products(session, market.id, seen_billz_ids)
    return result


async def sync_billz_products(session: AsyncSession, bot=None) -> dict:
    """
    Billz'ga bog'langan (o'zining `billz_secret_key`i bor) HAR BIR do'kon
    uchun, o'sha do'konning O'Z KALITI bilan, mahsulotlar ro'yxatini to'liq
    tortib oladi va bazani Billz bilan mos qiladi (qo'shish/yangilash/
    deaktivatsiya). Qaytaradi: {"shops", "created", "updated",
    "deactivated", "errors"}.
    """
    if not settings.BILLZ_SYNC_ENABLED:
        raise RuntimeError("Billz funksiyasi o'chirilgan (.env: BILLZ_SYNC_ENABLED=false)")

    linked_markets = await get_markets_linked_to_billz(session)
    stats = {"shops": len(linked_markets), "created": 0, "updated": 0, "deactivated": 0, "errors": []}

    for market in linked_markets:
        try:
            result = await _sync_one_market(session, market, bot=bot)
            stats["created"] += result["created"]
            stats["updated"] += result["updated"]
            stats["deactivated"] += result["deactivated"]
        except Exception as exc:  # noqa: BLE001 — bitta do'kon xato bersa ham qolganlari davom etsin
            logger.exception("Billz sinxronizatsiyasida xato (do'kon: %s)", market.name)
            stats["errors"].append(f"{market.name}: {exc}")

    return stats


async def billz_sync_loop(bot=None) -> None:
    """Fon rejimida (background task) ishlaydigan davriy sinxronlash tsikli.
    `main.py` ichidan `asyncio.create_task(billz_sync_loop(bot))` bilan
    ishga tushiriladi — faqat BILLZ_SYNC_ENABLED=true bo'lsa."""
    from bot.database.engine import async_session_maker

    if not settings.BILLZ_SYNC_ENABLED:
        return

    logger.info("Billz sinxronizatsiya tsikli ishga tushdi (har %s daqiqada)", settings.BILLZ_SYNC_INTERVAL_MINUTES)

    while True:
        try:
            async with async_session_maker() as session:
                stats = await sync_billz_products(session, bot=bot)
                logger.info("Billz sinxronizatsiya yakunlandi: %s", stats)
        except Exception:
            logger.exception("Billz sinxronizatsiya tsiklida kutilmagan xato")

        await asyncio.sleep(settings.BILLZ_SYNC_INTERVAL_MINUTES * 60)
