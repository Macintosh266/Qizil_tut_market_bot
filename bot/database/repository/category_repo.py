from sqlalchemy import func, select
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


# ==================== Kategoriyalarni ALOHIDA boshqarish (admin panel) ====================

async def create_category(session: AsyncSession, name: str) -> CategoryModel:
    category = CategoryModel(name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def get_category(session: AsyncSession, category_id: int) -> CategoryModel | None:
    return await session.get(CategoryModel, category_id)


async def get_category_by_name(session: AsyncSession, name: str) -> CategoryModel | None:
    result = await session.execute(select(CategoryModel).where(CategoryModel.name == name))
    return result.scalar_one_or_none()


async def get_all_categories(session: AsyncSession) -> list[CategoryModel]:
    result = await session.execute(select(CategoryModel).order_by(CategoryModel.name))
    return list(result.scalars().all())


async def count_products_in_category(session: AsyncSession, category_id: int) -> int:
    from bot.models import ProductsModel

    result = await session.execute(
        select(func.count())
        .select_from(ProductsModel)
        .where(ProductsModel.category_id == category_id, ProductsModel.is_active.is_(True))
    )
    return result.scalar_one()


async def delete_category(session: AsyncSession, category: CategoryModel) -> None:
    await session.delete(category)
    await session.commit()
