from aiogram import Router

from bot.handlers.user.cart import router as cart_router
from bot.handlers.user.checkout import router as checkout_router
from bot.handlers.user.feedback import router as feedback_router
from bot.handlers.user.profile import router as profile_router
from bot.handlers.user.settings import router as settings_router
from bot.handlers.user.shopping import router as shopping_router


def get_user_router() -> Router:
    router = Router(name="user")
    router.include_router(shopping_router)
    router.include_router(cart_router)
    router.include_router(checkout_router)
    router.include_router(profile_router)
    router.include_router(feedback_router)
    router.include_router(settings_router)
    return router
