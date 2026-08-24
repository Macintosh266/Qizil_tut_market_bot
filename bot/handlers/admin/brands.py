from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.brand_repo import (
    create_brand,
    delete_brand,
    get_all_brands,
    get_brand,
    get_brand_by_name,
)
from bot.filters import IsAdmin, IsSuperAdmin
from bot.handlers.admin.base import CONFIRM_TEXTS, btn_texts, finish
from bot.keyboards.admin_kb import brands_select_kb, cancel_kb, confirm_kb
from bot.lexicons import get_employe_text
from bot.states import AdminPanelStates

router = Router(name="admin_brands")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ==================== BREND BOSHQARUVI — admin panel (tugmalar) ====================
# Diqqat: bu bo'lim faqat SUPER_ADMIN uchun (base.py'dagi navigatsiya ham
# shunday cheklangan), chunki brendlar barcha do'konlar uchun umumiy.

@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("add_brand_btn")))
async def start_add_brand(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_add_brand_name)
    await message.answer(get_employe_text("add_brand_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_brand_name, F.text)
async def process_add_brand_name(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    name = message.text.strip()
    existing = await get_brand_by_name(session, name)
    if existing:
        await message.answer(get_employe_text("brand_exists", lang))
        return

    brand = await create_brand(session, name)
    await finish(message, state, lang, get_employe_text("brand_added", lang, name=brand.name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("delete_brand_btn")))
async def start_delete_brand(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    brands = await get_all_brands(session)
    if not brands:
        await message.answer(get_employe_text("no_brands", lang))
        return
    await message.answer(
        get_employe_text("choose_brand_prompt", lang),
        reply_markup=brands_select_kb(brands, "db_pick", lang),
    )


@router.callback_query(F.data.startswith("db_pick:"))
async def pick_delete_brand(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    brand_id = int(callback.data.split(":")[1])
    brand = await get_brand(session, brand_id)
    if not brand:
        await callback.answer(get_employe_text("no_brands", lang), show_alert=True)
        return

    await state.update_data(brand_id=brand.id)
    await state.set_state(AdminPanelStates.waiting_confirm_delete_brand)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_employe_text("confirm_delete_brand", lang, name=brand.name), reply_markup=confirm_kb(lang)
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_confirm_delete_brand, F.text.func(lambda t: t in CONFIRM_TEXTS))
async def process_confirm_delete_brand(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    brand = await get_brand(session, data["brand_id"])
    if brand:
        await delete_brand(session, brand)
    await finish(message, state, lang, get_employe_text("brand_deleted", lang, name=brand.name if brand else ""))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("brand_list_btn")))
async def show_brand_list(message: Message, session: AsyncSession, lang: str):
    brands = await get_all_brands(session)
    if not brands:
        await message.answer(get_employe_text("no_brands", lang))
        return
    lines = [f"• {b.name}" for b in brands]
    await message.answer("\n".join(lines))
