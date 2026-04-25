"""APScheduler background jobs."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.db.database import AsyncSessionLocal
from backend.db.models import Watchlist, Product, PriceHistory
from backend.scrapers.ml_scraper import search_ml
from backend.scrapers.amazon_scraper import search_amazon

scheduler = AsyncIOScheduler()


async def scrape_watchlist():
    print("[scheduler] Starting watchlist scrape...")
    async with AsyncSessionLocal() as session:
        rows = await session.scalars(
            select(Watchlist).options(selectinload(Watchlist.product))
        )
        watchlist = rows.all()
        for w in watchlist:
            p = w.product
            try:
                if p.source == "mercadolibre":
                    results = await search_ml(p.title, limit=1)
                else:
                    results = await search_amazon(p.title, limit=1)
                if results:
                    session.add(PriceHistory(
                        product_id=p.id,
                        price=results[0]["price"],
                        currency=results[0]["currency"],
                    ))
            except Exception as e:
                print(f"[scheduler] Error scraping {p.id}: {e}")
        await session.commit()
    print(f"[scheduler] Done — {len(watchlist)} products checked")


def start_scheduler():
    scheduler.add_job(scrape_watchlist, IntervalTrigger(hours=6), id="scrape_watchlist", replace_existing=True)
    scheduler.start()
    print("[scheduler] Started — scraping every 6h")
