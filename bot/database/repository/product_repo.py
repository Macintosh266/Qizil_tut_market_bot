from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import ProductsModel


async def get_products_by_category(
    session: AsyncSession, market_id: int, category_id: int
) -> list[ProductsModel]:
    result = await session.execute(
        select(ProductsModel).where(
            ProductsModel.market_id == market_id,
            ProductsModel.category_id == category_id,
            ProductsModel.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def search_products(
    session: AsyncSession, market_id: int, query: str
) -> list[ProductsModel]:
    result = await session.execute(
        select(ProductsModel).where(
            ProductsModel.market_id == market_id,
            ProductsModel.is_active.is_(True),
            ProductsModel.name.ilike(f"%{query}%"),
        )
    )
    return list(result.scalars().all())


async def get_product(session: AsyncSession, product_id: int) -> ProductsModel | None:
    return await session.get(ProductsModel, product_id)


async def get_product_by_market_and_name(
    session: AsyncSession, market_id: int, name: str
) -> ProductsModel | None:
    result = await session.execute(
        select(ProductsModel).where(
            ProductsModel.market_id == market_id,
            ProductsModel.name == name,
            ProductsModel.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def create_product(
    session: AsyncSession,
    market_id: int,
    category_id: int,
    name: str,
    price: float,
    stock: int,
    discription: str | None = None,
    image_file_id: str | None = None,
) -> ProductsModel:
    product = ProductsModel(
        market_id=market_id,
        category_id=category_id,
        name=name,
        price=price,
        stock=stock,
        discription=discription,
        image_file_id=image_file_id,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def add_or_restock_product(
    session: AsyncSession,
    market_id: int,
    category_id: int,
    name: str,
    price: float,
    stock_to_add: int,
    discription: str | None = None,
    image_file_id: str | None = None,
) -> tuple[ProductsModel, bool]:
    """
    Agar shu do'konda xuddi shu nomdagi (faol) mahsulot ALLAQACHON bo'lsa —
    dublikat yaratmaydi, balki uning miqdorini oshiradi va narxi/kategoriyasini
    yangilaydi. Qaytaradi: (product, created) — created=False bo'lsa, bu
    mavjud mahsulot miqdori oshirilgan, yangi qator yaratilmagan.
    """
    existing = await get_product_by_market_and_name(session, market_id, name)
    if existing:
        existing.stock += stock_to_add
        existing.price = price
        existing.category_id = category_id
        if image_file_id:
            existing.image_file_id = image_file_id
        if discription:
            existing.discription = discription
        await session.commit()
        await session.refresh(existing)
        return existing, False

    product = await create_product(
        session,
        market_id=market_id,
        category_id=category_id,
        name=name,
        price=price,
        stock=stock_to_add,
        discription=discription,
        image_file_id=image_file_id,
    )
    return product, True


async def delete_product(session: AsyncSession, product: ProductsModel) -> None:
    product.is_active = False
    await session.commit()


async def decrease_stock(session: AsyncSession, product: ProductsModel, quantity: int) -> None:
    product.stock = max(0, product.stock - quantity)
    await session.commit()


async def get_products_by_market(session: AsyncSession, market_id: int) -> list[ProductsModel]:
    """Do'kondagi barcha (kategoriyasidan qat'i nazar) faol mahsulotlar ro'yxati."""
    result = await session.execute(
        select(ProductsModel).where(
            ProductsModel.market_id == market_id, ProductsModel.is_active.is_(True)
        )
    )
    return list(result.scalars().all())


async def update_product_price(session: AsyncSession, product: ProductsModel, new_price: float) -> None:
    product.price = new_price
    await session.commit()


async def update_product_name(session: AsyncSession, product: ProductsModel, new_name: str) -> None:
    product.name = new_name
    await session.commit()


async def update_product_description(session: AsyncSession, product: ProductsModel, new_description: str) -> None:
    product.discription = new_description
    await session.commit()


async def update_product_stock(session: AsyncSession, product: ProductsModel, new_stock: int) -> None:
    product.stock = new_stock
    await session.commit()


async def update_product_category(session: AsyncSession, product: ProductsModel, new_category_id: int) -> None:
    product.category_id = new_category_id
    await session.commit()


async def update_product_photo(session: AsyncSession, product: ProductsModel, image_file_id: str) -> None:
    product.image_file_id = image_file_id
    await session.commit()


async def get_stock_summary(session: AsyncSession, market_id: int | None = None) -> tuple[int, float]:
    """(omborda qolgan umumiy dona, umumiy summa) ni qaytaradi. market_id berilsa — faqat shu do'kon."""
    query = select(ProductsModel).where(ProductsModel.is_active.is_(True))
    if market_id is not None:
        query = query.where(ProductsModel.market_id == market_id)
    result = await session.execute(query)
    products = result.scalars().all()
    total_qty = sum(p.stock for p in products)
    total_sum = sum(p.stock * float(p.price) for p in products)
    return total_qty, total_sum
