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
