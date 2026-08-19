from aiogram import Router

from bot.handlers.admin.ban import router as ban_router
from bot.handlers.admin.panel import router as panel_router


def get_admin_router() -> Router:
    router = Router(name="admin")
    # Diqqat: eski komanda-asosli routerlar (/add_admin, /add_staff,
    # /add_market, /add_product, /statistic) OLIB TASHLANDI — ular do'kon
    # (market_id) cheklovini chetlab o'tar edi. Endi BARCHA admin amallari
    # faqat panel_router orqali (tugmalar orqali, do'konga bog'langan holda)
    # bajariladi. /ban va /unban esa do'konga bog'liq emas, shuning uchun
    # komanda ko'rinishida ham xavfsiz qoladi.
    router.include_router(panel_router)
    router.include_router(ban_router)
    return router
