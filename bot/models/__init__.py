# Barcha modellar shu yerda import qilinadi, shunda SQLAlchemy mapper
# registry ularning orasidagi relationship'larni to'g'ri sozlay oladi.
from bot.models.user_model import Address, UserModel
from bot.models.market_model import MarketModel
from bot.models.category_model import CategoryModel
from bot.models.brand_model import BrandModel
from bot.models.product_model import ProductsModel
from bot.models.order_model import OrderItemModel, OrderModel
from bot.models.statistic_model import StatisticModel
from bot.models.feedback_model import FeedbackModel

__all__ = [
    "UserModel",
    "Address",
    "MarketModel",
    "CategoryModel",
    "BrandModel",
    "ProductsModel",
    "OrderModel",
    "OrderItemModel",
    "StatisticModel",
    "FeedbackModel",
]
