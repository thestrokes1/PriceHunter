import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import Product, PriceHistory, Category
from backend.scrapers.ml_scraper import search_ml
from backend.scrapers.amazon_scraper import search_amazon

router = APIRouter(prefix="/search", tags=["search"])


async def _upsert_product(session: AsyncSession, data: dict, category_id: int | None) -> Product:
    existing = await session.scalar(select(Product).where(Product.url == data["url"]))
    if existing:
        product = existing
    else:
        product = Product(
            title=data["title"],
            url=data["url"],
            source=data["source"],
            category_id=category_id,
            imagen_url=data.get("imagen_url"),
            rating=data.get("rating"),
            reviews=data.get("reviews"),
        )
        session.add(product)
        await session.flush()

    entry = PriceHistory(
        product_id=product.id,
        price=data["price"],
        currency=data["currency"],
    )
    session.add(entry)
    return product


@router.get("")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    cat: str | None = Query(None, description="Category slug"),
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    category_id = None
    if cat:
        category_id = await db.scalar(select(Category.id).where(Category.slug == cat))

    ml_results, amazon_results = await asyncio.gather(
        search_ml(q, limit),
        search_amazon(q, limit),
    )

    saved_ml = []
    for item in ml_results:
        p = await _upsert_product(db, item, category_id)
        saved_ml.append({**item, "id": p.id})

    saved_amazon = []
    for item in amazon_results:
        p = await _upsert_product(db, item, category_id)
        saved_amazon.append({**item, "id": p.id})

    return {"query": q, "ml": saved_ml, "amazon": saved_amazon}
