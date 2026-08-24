from aiogram import Router

from bot.handlers.admin import get_admin_router
from bot.handlers.common import get_common_router

# STAFF funksiyasi VAQTINCHA UZIB QO'YILGAN (kod o'chirilmagan — pastdagi
# import va include_router qatorlarini qayta yoqish uchun izohdan chiqarish
# kifoya). Buni yoqsangiz, bot/handlers/admin/__init__.py faylidagi
# "Xodimlar boshqaruvi" bo'limini ham qayta yoqishni unutmang.
# from bot.handlers.staff import get_staff_router
from bot.handlers.user import get_user_router
from bot.handlers.common.others import router as other_router


def get_main_router() -> Router:
    router = Router(name="main")
    # Tartib muhim: /start va /help har qanday holatda (hatto admin panel
    # FSM jarayonida "qotib qolingan" bo'lsa ham) ishlashi kerak, shuning
    # uchun common router BIRINCHI bo'lib tekshiriladi. Undan keyin
    # admin komandalar (IsAdmin filter bilan himoyalangan), so'ng xaridor oqimi.
    router.include_router(get_common_router())
    router.include_router(get_admin_router())
    # STAFF funksiyasi vaqtincha uzib qo'yilgan — yuqoridagi izohga qarang
    # router.include_router(get_staff_router())
    router.include_router(get_user_router())

    router.include_router(other_router)
    return router
