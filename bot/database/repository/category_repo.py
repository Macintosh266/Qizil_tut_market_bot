from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import CategoryModel


async def get_or_create_category(session: AsyncSession, name: str) -> CategoryModel:
    result = await session.execute(select(CategoryModel).where(CategoryModel.name == name))
    category = result.scalar_one_or_none()
    if category:
        return category

    category = CategoryModel(name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def get_categories_by_market(session: AsyncSession, market_id: int) -> list[CategoryModel]:
    # Kategoriyalar do'kon bo'yicha emas, mahsulot orqali bog'lanadi;
    # shu do'konda kamida bitta faol mahsuloti bor kategoriyalarni qaytaramiz.
    from bot.models import ProductsModel

    result = await session.execute(
        select(CategoryModel)
        .join(ProductsModel, ProductsModel.category_id == CategoryModel.id)
        .where(ProductsModel.market_id == market_id, ProductsModel.is_active.is_(True))
        .distinct()
    )
    return list(result.scalars().all())
