from aiogram import Router

from bot.handlers.admin.admins import router as admins_router
from bot.handlers.admin.ban import router as ban_router
from bot.handlers.admin.base import router as base_router
from bot.handlers.admin.markets import router as markets_router
from bot.handlers.admin.products import router as products_router
from bot.handlers.admin.staff import router as staff_router
from bot.handlers.admin.statistics import router as statistics_router


def get_admin_router() -> Router:
    router = Router(name="admin")
    router.include_router(base_router)
    router.include_router(admins_router)
    router.include_router(staff_router)
    router.include_router(ban_router)
    router.include_router(markets_router)
    router.include_router(products_router)
    router.include_router(statistics_router)
    return router