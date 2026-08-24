from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    choosing_language = State()
    waiting_phone = State()


class Shopping(StatesGroup):
    searching_product = State()
    waiting_quantity = State()


class Checkout(StatesGroup):
    waiting_address = State()
    confirm = State()


class Cart(StatesGroup):
    waiting_quantity = State()


class Feedback(StatesGroup):
    waiting_text = State()


class SettingsStates(StatesGroup):
    waiting_new_name = State()
    waiting_new_address = State()


class AdminPanelStates(StatesGroup):
    """Admin panel submenyulari orqali (reply-keyboard) amallarni bajarish uchun."""

    # Admin boshqaruvi
    waiting_add_admin_id = State()
    waiting_delete_admin_id = State()

    # Ishchi boshqaruvi
    waiting_add_staff_id = State()
    waiting_delete_staff_id = State()

    # Ban/Unban
    waiting_ban_id = State()
    waiting_unban_id = State()

    # Do'kon boshqaruvi
    waiting_add_market_name = State()
    waiting_add_market_address = State()
    waiting_delete_market_name = State()
    waiting_confirm_delete_market = State()

    # Mahsulot qo'shish
    waiting_add_product_market = State()
    waiting_add_product_name = State()
    waiting_add_product_qty = State()
    waiting_add_product_price = State()
    waiting_add_product_category = State()
    waiting_add_product_photo = State()

    # Mahsulot o'chirish
    waiting_delete_product_market = State()
    waiting_delete_product_name = State()
    waiting_confirm_delete_product = State()

    # Mahsulot narxini tahrirlash
    waiting_edit_price_market = State()
    waiting_edit_price_product = State()
    waiting_edit_price_new_value = State()

    # Mahsulotning boshqa maydonlarini tahrirlash
    waiting_edit_name_value = State()
    waiting_edit_description_value = State()
    waiting_edit_stock_value = State()
    waiting_edit_category_value = State()
    waiting_edit_photo_value = State()

    # Ro'yxat uzun bo'lganda tugma o'rniga yozib qidirish uchun
    searching_market = State()
    searching_product = State()
    searching_user = State()

    # Statistika uchun maxsus davr yozib kiritish (tugmalar bilan bir qatorda)
    waiting_statistic_period = State()

    # Kategoriya boshqaruvi (alohida bo'lim)
    waiting_add_category_name = State()
    waiting_confirm_delete_category = State()

    # Brend boshqaruvi (alohida bo'lim)
    waiting_add_brand_name = State()
    waiting_confirm_delete_brand = State()

    # Mahsulot qo'shish jarayonida "+ Yangi ..." tugmasi bosilganda
    # (brend/kategoriya ro'yxatida yo'q nomni shu yerdan yozib kiritadi)
    waiting_new_brand_inline = State()
    waiting_new_category_inline = State()