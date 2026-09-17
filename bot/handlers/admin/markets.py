from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.repository.market_repo import (
    create_market,
    delete_market,
    get_all_markets,
    get_market,
    get_market_by_name,
    get_markets_linked_to_billz,
    get_unlinked_markets,
    reactivate_market,
    set_market_billz_credentials,
)
from bot.filters import IsAdmin, IsSuperAdmin
from bot.handlers.admin.base import CONFIRM_TEXTS, btn_texts, finish, track_list_message
from bot.keyboards.admin_kb import cancel_kb, confirm_kb, has_billz_kb, markets_select_kb
from bot.lexicons import get_employe_text
from bot.services.billz_sync import sync_billz_products, verify_billz_key
from bot.states import AdminPanelStates

router = Router(name="admin_markets")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ==================== DO'KON BOSHQARUVI — admin panel (tugmalar) ====================

@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("add_market_btn")))
async def start_add_market(message: Message, state: FSMContext, lang: str):
    await state.set_state(AdminPanelStates.waiting_add_market_name)
    await message.answer(get_employe_text("add_market_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_market_name, IsSuperAdmin(), F.text)
async def process_market_name(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    name = message.text.strip()
    existing = await get_market_by_name(session, name)

    if existing and existing.is_active:
        # Faol do'kon shu nom bilan allaqachon bor — rad etamiz
        await message.answer(get_employe_text("market_name_exists", lang))
        return

    # existing bo'lsa (avval o'chirilgan) — keyingi bosqichda qayta
    # faollashtiramiz; bo'lmasa, yangi do'kon yaratiladi.
    await state.update_data(
        market_name=name,
        reactivate_market_id=existing.id if existing else None,
    )
    await state.set_state(AdminPanelStates.waiting_add_market_address)
    await message.answer(get_employe_text("add_market_address_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(AdminPanelStates.waiting_add_market_address, IsSuperAdmin(), F.text)
async def process_market_address(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    address = message.text.strip()
    reactivate_market_id = data.get("reactivate_market_id")

    if reactivate_market_id:
        existing = await get_market(session, reactivate_market_id)
        market = await reactivate_market(session, existing, address)
    else:
        market = await create_market(session, name=data["market_name"], address=address)

    # Do'kon yaratildi — endi Billz tizimi bormi-yo'qmi so'raymiz. Agar
    # "Ha" desa, o'sha yerning o'zida kalitni so'raymiz (alohida
    # "🔗 Billz bilan bog'lash" bosqichiga o'tish shart emas).
    await state.set_data({})
    await state.set_state(None)
    await message.answer(
        get_employe_text("market_added", lang, name=market.name) + "\n\n" + get_employe_text("ask_has_billz", lang),
        reply_markup=has_billz_kb(market.id, lang),
    )


@router.callback_query(IsSuperAdmin(), F.data.startswith("new_market_billz:no:"))
async def skip_billz_for_new_market(callback: CallbackQuery, lang: str):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(get_employe_text("market_setup_done", lang))
    await callback.answer()


@router.callback_query(IsSuperAdmin(), F.data.startswith("new_market_billz:yes:"))
async def ask_billz_key_for_new_market(callback: CallbackQuery, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[2])
    await state.update_data(link_market_id=market_id)
    await state.set_state(AdminPanelStates.waiting_billz_secret_key)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(get_employe_text("enter_billz_secret_key_short", lang), reply_markup=cancel_kb(lang))
    await callback.answer()


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("delete_market_btn")))
async def start_delete_market(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    await state.update_data(search_context="del_market")
    await state.set_state(AdminPanelStates.searching_market)
    sent = await message.answer(
        get_employe_text("choose_market_prompt", lang) + get_employe_text("search_or_choose_hint", lang),
        reply_markup=markets_select_kb(markets, "del_market_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(IsSuperAdmin(), F.data.startswith("del_market_pick:"))
async def pick_delete_market(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return
    await state.update_data(market_id=market.id)
    await state.set_state(AdminPanelStates.waiting_confirm_delete_market)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_employe_text("confirm_delete_market", lang, name=market.name), reply_markup=confirm_kb(lang)
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_confirm_delete_market, IsSuperAdmin(), F.text.func(lambda t: t in CONFIRM_TEXTS))
async def process_confirm_delete_market(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    market = await get_market(session, data["market_id"])
    if market:
        await delete_market(session, market)
    await finish(message, state, lang, get_employe_text("market_deleted", lang, name=market.name if market else ""))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("market_list_btn")))
async def show_market_list(message: Message, session: AsyncSession, lang: str):
    markets = await get_all_markets(session)
    if not markets:
        await message.answer(get_employe_text("empty_list", lang))
        return
    lines = [f"{m.name} — {m.address}" for m in markets]
    await message.answer("\n".join(lines))


# ==================== Billz.io INTEGRATSIYASI ====================
# Har bir do'kon Billz'da o'zining alohida akkauntiga (alohida API
# kalitiga) ega — shuning uchun bog'lash "do'kon tanlash -> o'sha
# do'konning Billz kalitini yozib kiritish" tarzida ishlaydi (Billz
# tomonidan "shop" tanlash bosqichi yo'q, chunki kalitning o'zi bitta
# do'konga tegishli).

@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("link_billz_btn")))
async def start_link_billz(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    if not settings.BILLZ_SYNC_ENABLED:
        await message.answer(get_employe_text("billz_not_configured", lang))
        return

    markets = await get_unlinked_markets(session)
    if not markets:
        await message.answer(get_employe_text("no_unlinked_markets", lang))
        return

    sent = await message.answer(
        get_employe_text("choose_market_to_link", lang),
        reply_markup=markets_select_kb(markets, "link_market_pick", lang),
    )
    await track_list_message(state, sent)


@router.callback_query(IsSuperAdmin(), F.data.startswith("link_market_pick:"))
async def pick_market_to_link(callback: CallbackQuery, session: AsyncSession, lang: str, state: FSMContext):
    market_id = int(callback.data.split(":")[1])
    market = await get_market(session, market_id)
    if not market:
        await callback.answer(get_employe_text("market_not_found", lang), show_alert=True)
        return

    await state.update_data(link_market_id=market.id)
    await state.set_state(AdminPanelStates.waiting_billz_secret_key)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_employe_text("enter_billz_secret_key", lang, market=market.name), reply_markup=cancel_kb(lang)
    )
    await callback.answer()


@router.message(AdminPanelStates.waiting_billz_secret_key, IsSuperAdmin(), F.text)
async def process_billz_secret_key(message: Message, session: AsyncSession, lang: str, state: FSMContext):
    data = await state.get_data()
    market_id = data.get("link_market_id")
    market = await get_market(session, market_id) if market_id else None
    if not market:
        await finish(message, state, lang, get_employe_text("market_not_found", lang))
        return

    secret_key = message.text.strip()

    # Ochiq (plaintext) API kalitini chatda saqlab qolmaslik uchun,
    # foydalanuvchi yuborgan xabarni darhol o'chiramiz.
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer(get_employe_text("billz_key_checking", lang))

    if not await verify_billz_key(secret_key):
        await message.answer(get_employe_text("billz_key_invalid", lang))
        return  # xato bo'lsa, holatda qolib, qayta kiritishga imkon beramiz

    await set_market_billz_credentials(session, market, secret_key)
    await finish(message, state, lang, get_employe_text("market_linked_to_billz", lang, market=market.name))


@router.message(IsSuperAdmin(), F.text.func(lambda t: t in btn_texts("sync_billz_btn")))
async def trigger_billz_sync(message: Message, session: AsyncSession, lang: str, bot: Bot):
    if not settings.BILLZ_SYNC_ENABLED:
        await message.answer(get_employe_text("billz_not_configured", lang))
        return

    linked = await get_markets_linked_to_billz(session)
    if not linked:
        await message.answer(get_employe_text("billz_sync_no_shops", lang))
        return

    await message.answer(get_employe_text("billz_sync_started", lang))
    try:
        stats = await sync_billz_products(session, bot=bot)
    except Exception as exc:
        await message.answer(get_employe_text("billz_sync_error", lang, error=str(exc)))
        return

    errors_text = ""
    if stats["errors"]:
        errors_text = "\n⚠️ " + "; ".join(stats["errors"])

    await message.answer(
        get_employe_text(
            "billz_sync_result", lang,
            shops=stats["shops"], created=stats["created"], updated=stats["updated"],
            deactivated=stats["deactivated"], errors=errors_text,
        )
    )