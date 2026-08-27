from aiogram import Router

from bot.handlers.admin import get_admin_router
from bot.handlers.common import get_common_router

# STAFF funksiyasi vaqtincha uzib qo'yilgan (kod o'chirilmagan — pastdagi
# qatorni izohdan chiqarish kifoya). bot/handlers/admin/__init__.py'dagi
# "Xodimlar boshqaruvi"ni ham qayta yoqish kerak bo'ladi.
# from bot.handlers.staff import get_staff_router
from bot.handlers.user import get_user_router
from bot.handlers.common.others import router as other_router


def get_main_router() -> Router:
    router = Router(name="main")

    router.include_router(get_common_router())
    router.include_router(get_admin_router())
    # STAFF funksiyasi vaqtincha uzib qo'yilgan
    # router.include_router(get_staff_router())
    router.include_router(get_user_router())

    router.include_router(other_router)
    return router
