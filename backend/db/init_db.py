"""Run once to create tables and seed categories."""
import asyncio
from sqlalchemy import select
from backend.db.database import engine, AsyncSessionLocal, Base
from backend.db.models import Category


CATEGORIES = [
    {"nombre": "Tecnología",   "slug": "tecnologia",   "icono": "💻", "color": "#3b82f6"},
    {"nombre": "Celulares",    "slug": "celulares",    "icono": "📱", "color": "#8b5cf6"},
    {"nombre": "Motos",        "slug": "motos",        "icono": "🏍️", "color": "#f59e0b"},
    {"nombre": "Autos",        "slug": "autos",        "icono": "🚗", "color": "#ef4444"},
    {"nombre": "Instrumentos", "slug": "instrumentos", "icono": "🎸", "color": "#10b981"},
    {"nombre": "Hogar",        "slug": "hogar",        "icono": "🏠", "color": "#6b7280"},
    {"nombre": "Deportes",     "slug": "deportes",     "icono": "⚽", "color": "#f97316"},
    {"nombre": "Ropa",         "slug": "ropa",         "icono": "👕", "color": "#ec4899"},
]


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Tables created")

    async with AsyncSessionLocal() as session:
        for cat in CATEGORIES:
            exists = await session.scalar(select(Category).where(Category.slug == cat["slug"]))
            if not exists:
                session.add(Category(**cat))
        await session.commit()
    print(f"[OK] {len(CATEGORIES)} categories seeded")


if __name__ == "__main__":
    asyncio.run(init())
