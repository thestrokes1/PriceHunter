from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from backend.db.database import get_db
from backend.db.models import Product, PriceHistory, Watchlist, Category
from backend.scrapers.ml_scraper import search_ml
from backend.scrapers.amazon_scraper import search_amazon

router = APIRouter(prefix="/admin", tags=["admin"])


class AddProductBody(BaseModel):
    url: str
    category_id: int | None = None
    source: str  # 'mercadolibre' | 'amazon'


@router.get("/products")
async def list_products(
    source: str | None = None,
    cat: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Product).options(selectinload(Product.price_history), selectinload(Product.category))
    if source:
        q = q.where(Product.source == source)
    if cat:
        q = q.join(Category).where(Category.slug == cat)
    rows = await db.scalars(q.order_by(Product.created_at.desc()))
    products = rows.all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "url": p.url,
            "source": p.source,
            "category": p.category.nombre if p.category else None,
            "current_price": p.price_history[-1].price if p.price_history else None,
            "currency": p.price_history[-1].currency if p.price_history else None,
            "price_count": len(p.price_history),
            "imagen_url": p.imagen_url,
            "created_at": p.created_at.isoformat(),
        }
        for p in products
    ]


@router.post("/products", status_code=201)
async def add_product(body: AddProductBody, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(Product).where(Product.url == body.url))
    if existing:
        raise HTTPException(409, "Product already tracked")

    if body.source == "mercadolibre":
        results = await search_ml("", limit=1)
    else:
        results = await search_amazon("", limit=1)

    product = Product(
        title=body.url,
        url=body.url,
        source=body.source,
        category_id=body.category_id,
    )
    db.add(product)
    return {"ok": True, "url": body.url}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_products = await db.scalar(select(func.count()).select_from(Product))
    total_watchlist = await db.scalar(select(func.count()).select_from(Watchlist))
    total_prices = await db.scalar(select(func.count()).select_from(PriceHistory))
    last_scrape = await db.scalar(select(func.max(PriceHistory.scraped_at)))
    ml_count = await db.scalar(select(func.count()).select_from(Product).where(Product.source == "mercadolibre"))
    amazon_count = await db.scalar(select(func.count()).select_from(Product).where(Product.source == "amazon"))

    return {
        "total_products": total_products,
        "mercadolibre_products": ml_count,
        "amazon_products": amazon_count,
        "watchlist_items": total_watchlist,
        "total_price_records": total_prices,
        "last_scrape": last_scrape.isoformat() if last_scrape else None,
    }


@router.post("/scrape-all")
async def scrape_all(db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(
        select(Watchlist).options(selectinload(Watchlist.product))
    )
    watchlist = rows.all()
    scraped = 0
    errors = 0
    for w in watchlist:
        p = w.product
        try:
            if p.source == "mercadolibre":
                results = await search_ml(p.title, limit=1)
            else:
                results = await search_amazon(p.title, limit=1)
            if results:
                db.add(PriceHistory(product_id=p.id, price=results[0]["price"], currency=results[0]["currency"]))
                scraped += 1
            else:
                errors += 1
        except Exception as e:
            print(f"[scrape-all] Error on {p.id}: {e}")
            errors += 1

    return {"scraped": scraped, "errors": errors}
