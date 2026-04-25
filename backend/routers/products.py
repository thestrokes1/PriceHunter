from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.db.database import get_db
from backend.db.models import Product, PriceHistory
from backend.scrapers.ml_scraper import search_ml
from backend.scrapers.amazon_scraper import search_amazon

router = APIRouter(prefix="/products", tags=["products"])


def _product_dict(p: Product) -> dict:
    prices = [ph.price for ph in p.price_history]
    current = prices[-1] if prices else None
    price_30d_ago = prices[0] if prices else None
    change_pct = None
    if current and price_30d_ago and price_30d_ago != 0:
        change_pct = round((current - price_30d_ago) / price_30d_ago * 100, 2)

    return {
        "id": p.id,
        "title": p.title,
        "url": p.url,
        "source": p.source,
        "imagen_url": p.imagen_url,
        "rating": p.rating,
        "reviews": p.reviews,
        "category_id": p.category_id,
        "current_price": current,
        "currency": p.price_history[-1].currency if p.price_history else None,
        "price_change_pct": change_pct,
        "min_price": min(prices) if prices else None,
        "max_price": max(prices) if prices else None,
        "avg_price": round(sum(prices) / len(prices), 2) if prices else None,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await db.scalar(
        select(Product).where(Product.id == product_id).options(selectinload(Product.price_history))
    )
    if not p:
        raise HTTPException(404, "Product not found")
    return _product_dict(p)


@router.get("/{product_id}/history")
async def get_history(product_id: int, db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at)
    )
    history = rows.all()
    if not history:
        raise HTTPException(404, "No price history found")
    return [{"price": h.price, "currency": h.currency, "scraped_at": h.scraped_at.isoformat()} for h in history]


@router.post("/{product_id}/scrape")
async def force_scrape(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await db.scalar(select(Product).where(Product.id == product_id))
    if not p:
        raise HTTPException(404, "Product not found")

    if p.source == "mercadolibre":
        results = await search_ml(p.title, limit=1)
    else:
        results = await search_amazon(p.title, limit=1)

    if not results:
        return {"ok": False, "message": "Scraper returned no results"}

    entry = PriceHistory(product_id=p.id, price=results[0]["price"], currency=results[0]["currency"])
    db.add(entry)
    return {"ok": True, "new_price": results[0]["price"]}
