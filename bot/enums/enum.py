import enum


class UserRole(str, enum.Enum):
    USER = "user"
    STAFF = "staff"           # bitta do'konga tegishli ishchi
    ADMIN = "admin"           # bitta do'konning admini (market_id orqali bog'langan)
    SUPER_ADMIN = "super_admin"  # platforma darajasida - barcha do'konlarni boshqaradi


class Language(str, enum.Enum):
    UZ = "uz"
    RU = "ru"
    EN = "en"


class OrderStatus(str, enum.Enum):
    NEW = "new"                # yangi tushdi
    CONFIRMED = "confirmed"    # ishchi qabul qildi
    DELIVERING = "delivering"  # yetkazilmoqda
    DONE = "done"              # yakunlandi (yetkazildi / olib ketildi)
    CANCELED = "canceled"      # bekor qilindi


class DeliveryType(str, enum.Enum):
    PICKUP = "pickup"      # xaridor o'zi olib ketadi
    DELIVERY = "delivery"  # yetkazib beriladi
