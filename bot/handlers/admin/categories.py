from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repository.category_repo import (
    count_products_in_category,
    create_category,
    delete_category,
    get_all_categories,
    get_category,
    get_category_by_name,
)
from bot.filters import IsAdmin, IsSuperAdmin
from bot.handlers.admin.base import CONFIRM_TEXTS, btn_texts, finish
from bot.keyboards.admin_kb import cancel_kb, categories_select_kb, confirm_kb
from bot.lexicons import get_employe_text
from bot.states import AdminPanelStates

router = Router(name="admin_categories")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ==================== KATEGORIYA BOSHQARUVI — admin panel (tugmalar) ====================
# Diqqat: bu bo'lim faqat SUPER_ADMIN uchun (base.py'dagi navigatsiya ham
# shunday cheklangan), chunki kategoriyalar barcha do'konlar uchun umumiy.

@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("add_category_btn")))
async def start_add_category(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_add_category_name)
    await message.answer(get_employe_text("add_category_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_category_name, F.text)
async def process_add_category_name(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    name = message.text.strip()
    existing = await get_category_by_name(session, name)
    if existing:
        await message.answer(get_employe_text("category_exists", lang))
        return

    category = await create_category(session, name)
    await finish(message, state, lang, get_employe_text("category_added", lang, name=category.name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("delete_category_btn")))
async def start_delete_category(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    categories = await get_all_categories(session)
    if not categories:
        await message.answer(get_employe_text("no_categories", lang))
        return
    await message.answer(
        get_employe_text("choose_category_prompt", lang),
        reply_markup=categories_select_kb(categories, "dc_pick", lang),
    )


@router.callback_query(F.data.startswith("dc_pick:"))
async def pick_delete_category(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    category_id = int(callback.data.split(":")[1])
    category = await get_category(session, category_id)
    if not category:
        await callback.answer(get_employe_text("no_categories", lang), show_alert=True)
        return

    products_count = await count_products_in_category(session, category_id)
    if products_count > 0:
        await callback.answer(get_employe_text("category_has_products", lang), show_alert=True)
        return

    await state.update_data(category_id=category.id)
    await state.set_state(AdminPanelStates.waiting_confirm_delete_category)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_employe_text("confirm_delete_category", lang, name=category.name), reply_markup=confirm_kb(lang)
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_confirm_delete_category, F.text.func(lambda t: t in CONFIRM_TEXTS))
async def process_confirm_delete_category(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    category = await get_category(session, data["category_id"])
    if category:
        await delete_category(session, category)
    await finish(
        message, state, lang, get_employe_text("category_deleted", lang, name=category.name if category else "")
    )


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("category_list_btn")))
async def show_category_list(message: Message, session: AsyncSession, lang: str):
    categories = await get_all_categories(session)
    if not categories:
        await message.answer(get_employe_text("no_categories", lang))
        return
    lines = [f"• {c.name}" for c in categories]
    await message.answer("\n".join(lines))
