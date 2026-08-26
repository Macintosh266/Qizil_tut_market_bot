from aiogram import Router

from bot.handlers.admin.admins import router as admins_router
from bot.handlers.admin.ban import router as ban_router
from bot.handlers.admin.base import router as base_router
from bot.handlers.admin.brands import router as brands_router
from bot.handlers.admin.categories import router as categories_router
from bot.handlers.admin.feedbacks import router as feedbacks_router
from bot.handlers.admin.markets import router as markets_router
from bot.handlers.staff.orders import router as orders_router
from bot.handlers.admin.products import router as products_router

# STAFF (Xodimlar) boshqaruvi VAQTINCHA UZIB QO'YILGAN — kod o'chirilmagan,
# faqat ulanmagan. Qayta yoqish uchun pastdagi import va include_router
# qatorlarini izohdan chiqaring (va bot/handlers/__init__.py dagi
# get_staff_router() ni ham qayta yoqing).
# from bot.handlers.admin.staff import router as staff_router
from bot.handlers.admin.statistics import router as statistics_router


def get_admin_router() -> Router:
    router = Router(name="admin")
    router.include_router(base_router)
    router.include_router(admins_router)
    # STAFF boshqaruvi vaqtincha uzib qo'yilgan — yuqoridagi izohga qarang
    # router.include_router(staff_router)
    router.include_router(ban_router)
    router.include_router(markets_router)
    router.include_router(products_router)
    router.include_router(categories_router)
    router.include_router(brands_router)
    router.include_router(statistics_router)
    router.include_router(feedbacks_router)
    router.include_router(orders_router)
    return router