"""
Maxfiy ma'lumotlarni (masalan, har bir do'konning Billz API kaliti) bazada
OCHIQ MATN (plaintext) holda emas, SHIFRLANGAN holda saqlash uchun.

Fernet (simmetrik shifrlash: AES-128-CBC + HMAC-SHA256) ishlatiladi — bu
Python'dagi `cryptography` kutubxonasidagi eng sodda va ishonchli standart
usullardan biri. Fernet nafaqat shifrlaydi, balki ma'lumot yo'lda
o'zgartirilmaganini ham tekshiradi (authenticated encryption).

Kalitni generatsiya qilish (bir marta, serverni sozlashda):
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Natijani `.env` fayliga `ENCRYPTION_KEY=...` sifatida yozing va uni HECH
QACHON git'ga commit qilmang (`.gitignore`da `.env` allaqachon bor).

DIQQAT: agar `ENCRYPTION_KEY`ni yo'qotsangiz, avval shifrlangan barcha
ma'lumotlarni (Billz kalitlarini) qayta ochib bo'lmaydi — do'konlarni
qaytadan Billz bilan bog'lashga to'g'ri keladi. Kalitni xavfsiz joyda
zaxira nusxalab qo'ying.
"""

import logging

from cryptography.fernet import Fernet, InvalidToken

from bot.config import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    if not settings.ENCRYPTION_KEY:
        raise RuntimeError(
            "ENCRYPTION_KEY .env faylida sozlanmagan. Yaratish uchun: "
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    try:
        return Fernet(settings.ENCRYPTION_KEY.encode())
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "ENCRYPTION_KEY noto'g'ri formatda. U Fernet.generate_key() natijasi bo'lishi kerak."
        ) from exc


def encrypt_value(value: str) -> str:
    """Matnni shifrlaydi va bazaga yozish uchun mos (matn) satr qaytaradi."""
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_value(token: str) -> str | None:
    """
    Shifrlangan matnni ochadi. Agar `ENCRYPTION_KEY` noto'g'ri bo'lsa,
    matn buzilgan bo'lsa yoki (eski, migratsiyadan oldingi) oddiy matn
    bo'lib chiqsa — None qaytaradi (xato ko'tarilmaydi, chunki bu
    funksiya odatda sinxronizatsiya siklida chaqiriladi va bitta noto'g'ri
    kalit butun jarayonni to'xtatib qo'ymasligi kerak).
    """
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        logger.warning("Shifrni ochib bo'lmadi — ENCRYPTION_KEY noto'g'ri yoki ma'lumot shifrlanmagan (eski format)")
        return None
    except Exception:
        logger.exception("Shifrni ochishda kutilmagan xato")
        return None
