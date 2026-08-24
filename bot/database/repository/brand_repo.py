from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import BrandModel


async def create_brand(session: AsyncSession, name: str) -> BrandModel:
    brand = BrandModel(name=name)
    session.add(brand)
    await session.commit()
    await session.refresh(brand)
    return brand


async def get_brand(session: AsyncSession, brand_id: int) -> BrandModel | None:
    return await session.get(BrandModel, brand_id)


async def get_brand_by_name(session: AsyncSession, name: str) -> BrandModel | None:
    result = await session.execute(select(BrandModel).where(BrandModel.name == name))
    return result.scalar_one_or_none()


async def get_all_brands(session: AsyncSession) -> list[BrandModel]:
    result = await session.execute(select(BrandModel).order_by(BrandModel.name))
    return list(result.scalars().all())


async def delete_brand(session: AsyncSession, brand: BrandModel) -> None:
    # Kategoriyadan farqli o'laroq, brand_id ixtiyoriy (nullable) bo'lgani
    # uchun bu brendga tegishli mahsulotlarni bloklamasdan, ularning
    # brand_id'sini shunchaki bo'shatib, keyin brendni o'chiramiz.
    from bot.models import ProductsModel

    await session.execute(
        update(ProductsModel).where(ProductsModel.brand_id == brand.id).values(brand_id=None)
    )
    await session.delete(brand)
    await session.commit()


async def get_brands_by_market(session: AsyncSession, market_id: int) -> list[BrandModel]:
    """Shu do'konda kamida bitta faol mahsuloti bor brendlar ro'yxati —
    xaridor uchun brend-filtr tugmalarida ishlatiladi."""
    from bot.models import ProductsModel

    result = await session.execute(
        select(BrandModel)
        .join(ProductsModel, ProductsModel.brand_id == BrandModel.id)
        .where(ProductsModel.market_id == market_id, ProductsModel.is_active.is_(True))
        .distinct()
    )
    return list(result.scalars().all())
