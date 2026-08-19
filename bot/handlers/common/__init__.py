from aiogram import Router

from bot.handlers.common.start import router as start_router


def get_common_router() -> Router:
    router = Router(name="common")
    router.include_router(start_router)
    return router
