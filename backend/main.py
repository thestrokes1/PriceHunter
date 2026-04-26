from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from backend.db.database import engine, AsyncSessionLocal, Base
from backend.db.models import Category
from backend.db.init_db import init
from backend.routers import search, products, watchlist, admin
from backend.scheduler.jobs import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init()
    start_scheduler()
    yield
    from backend.scheduler.jobs import scheduler
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="PriceHunter API",
    description="Comparador de precios MercadoLibre + Amazon",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(products.router)
app.include_router(watchlist.router)
app.include_router(admin.router)


@app.get("/debug/fravega")
async def debug_fravega():
    """Temporary: diagnose what Render actually receives from Fravega."""
    from backend.scrapers.fravega_scraper import _curl_fetch, _parse_next_data, _parse_articles
    from bs4 import BeautifulSoup
    import json
    html = await _curl_fetch("televisor")
    if not html:
        return {"error": "empty response", "html_len": 0}
    soup = BeautifulSoup(html, "html.parser")
    nd = soup.find("script", id="__NEXT_DATA__")
    articles = soup.select("article")
    next_data_keys = []
    products_in_nd = 0
    if nd:
        try:
            data = json.loads(nd.string)
            apollo = data["props"]["pageProps"].get("__APOLLO_STATE__", {})
            root = apollo.get("ROOT_QUERY", {})
            items_key = next((k for k in root if k.startswith("items(")), None)
            if items_key:
                items = root[items_key]
                rk = next((k for k in items if k.startswith("results(")), None)
                if rk:
                    products_in_nd = len(items[rk])
            next_data_keys = list(apollo.keys())[:5]
        except Exception as e:
            next_data_keys = [f"parse error: {e}"]
    parsed = _parse_next_data(html, 5)
    return {
        "html_len": len(html),
        "has_next_data": nd is not None,
        "next_data_keys": next_data_keys,
        "products_in_apollo": products_in_nd,
        "articles_in_html": len(articles),
        "parsed_results": len(parsed),
        "sample": parsed[0] if parsed else None,
    }


@app.get("/health")
async def health():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "db": db_status, "version": "1.0.0"}


@app.get("/categories")
async def categories():
    async with AsyncSessionLocal() as session:
        rows = await session.scalars(select(Category).order_by(Category.id))
        cats = rows.all()
    return [{"id": c.id, "nombre": c.nombre, "slug": c.slug, "icono": c.icono, "color": c.color} for c in cats]
