"""APScheduler background jobs."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.db.database import AsyncSessionLocal
from backend.db.models import Watchlist, Product, PriceHistory
from backend.scrapers.ml_scraper import search_ml
from backend.scrapers.amazon_scraper import search_amazon
from backend.utils.mailer import send_price_alert

scheduler = AsyncIOScheduler()


async def scrape_watchlist():
    print("[scheduler] Starting watchlist scrape...")
    scraped = 0
    alerts_sent = 0

    async with AsyncSessionLocal() as session:
        rows = await session.scalars(
            select(Watchlist).options(
                selectinload(Watchlist.product).selectinload(Product.price_history)
            )
        )
        watchlist = rows.all()

        for w in watchlist:
            p = w.product
            try:
                if p.source == "mercadolibre":
                    results = await search_ml(p.title, limit=1)
                else:
                    results = await search_amazon(p.title, limit=1)

                if not results:
                    continue

                new_price = results[0]["price"]
                currency = results[0]["currency"]
                session.add(PriceHistory(product_id=p.id, price=new_price, currency=currency))
                scraped += 1

                # Check price alert
                if w.precio_al_agregar and w.precio_al_agregar > 0:
                    drop_pct = (w.precio_al_agregar - new_price) / w.precio_al_agregar * 100
                    if drop_pct >= w.alerta_pct:
                        sent = send_price_alert(
                            title=p.title,
                            source=p.source,
                            product_id=p.id,
                            current_price=new_price,
                            original_price=w.precio_al_agregar,
                            drop_pct=drop_pct,
                            currency=currency,
                        )
                        if sent:
                            alerts_sent += 1

            except Exception as e:
                print(f"[scheduler] Error scraping product {p.id}: {e}")

        await session.commit()

    print(f"[scheduler] Done — {scraped} scraped, {alerts_sent} alerts sent")


def start_scheduler():
    scheduler.add_job(
        scrape_watchlist,
        IntervalTrigger(hours=6),
        id="scrape_watchlist",
        replace_existing=True,
    )
    scheduler.start()
    print("[scheduler] Started — scraping every 6h")
