from aiogram import Router

from bot.handlers.staff.orders import router as orders_router


def get_staff_router() -> Router:
    router = Router(name="staff")
    router.include_router(orders_router)
    return router
