from aiogram import Router

from bot.handlers.admin import get_admin_router
from bot.handlers.common import get_common_router
from bot.handlers.staff import get_staff_router
from bot.handlers.user import get_user_router
from bot.handlers.common.others import router as other_router


def get_main_router() -> Router:
    router = Router(name="main")
    # Tartib muhim: /start va /help har qanday holatda (hatto admin panel
    # FSM jarayonida "qotib qolingan" bo'lsa ham) ishlashi kerak, shuning
    # uchun common router BIRINCHI bo'lib tekshiriladi. Undan keyin
    # admin/staff komandalar (IsAdmin/IsStaff filter bilan himoyalangan),
    # so'ng xaridor oqimi.
    router.include_router(get_common_router())
    router.include_router(get_admin_router())
    router.include_router(get_staff_router())
    router.include_router(get_user_router())

    router.include_router(other_router)
    return router
