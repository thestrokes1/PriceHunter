import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import Product, PriceHistory, Category
from backend.scrapers.ml_scraper import search_ml
from backend.scrapers.amazon_scraper import search_amazon
from backend.scrapers.fravega_scraper import search_fravega

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


async def _save_results(db: AsyncSession, results: list[dict], category_id: int | None) -> list[dict]:
    saved = []
    for item in results:
        p = await _upsert_product(db, item, category_id)
        saved.append({**item, "id": p.id})
    return saved


@router.get("")
async def search(
    q: str = Query(..., min_length=1),
    cat: str | None = Query(None),
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    category_id = None
    if cat:
        category_id = await db.scalar(select(Category.id).where(Category.slug == cat))

    # ML is fast (httpx). Fravega and Amazon use Playwright — run sequentially to avoid
    # event-loop conflicts on Windows. Fravega before Amazon (faster, no anti-bot).
    ml_results = await search_ml(q, limit)
    fravega_results = await search_fravega(q, limit)
    amazon_results = await search_amazon(q, limit)

    return {
        "query": q,
        "ml": await _save_results(db, ml_results, category_id),
        "fravega": await _save_results(db, fravega_results, category_id),
        "amazon": await _save_results(db, amazon_results, category_id),
    }
