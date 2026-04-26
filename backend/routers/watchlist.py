from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.db.database import get_db
from backend.db.models import Watchlist, Product, PriceHistory

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistCreate(BaseModel):
    product_id: int
    alerta_pct: float = Field(default=5.0, ge=0, le=100)


@router.get("")
async def list_watchlist(db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(
        select(Watchlist).options(
            selectinload(Watchlist.product).selectinload(Product.price_history)
        )
    )
    items = rows.all()
    result = []
    for w in items:
        p = w.product
        prices = [ph.price for ph in p.price_history]
        current = prices[-1] if prices else None
        change_pct = None
        if current and w.precio_al_agregar and w.precio_al_agregar != 0:
            change_pct = round((current - w.precio_al_agregar) / w.precio_al_agregar * 100, 2)
        result.append({
            "id": w.id,
            "product_id": p.id,
            "title": p.title,
            "url": p.url,
            "source": p.source,
            "imagen_url": p.imagen_url,
            "currency": p.price_history[-1].currency if p.price_history else None,
            "precio_al_agregar": w.precio_al_agregar,
            "current_price": current,
            "change_pct": change_pct,
            "alerta_pct": w.alerta_pct,
            "added_at": w.added_at.isoformat(),
        })
    return result


@router.post("", status_code=201)
async def add_to_watchlist(body: WatchlistCreate, db: AsyncSession = Depends(get_db)):
    product = await db.scalar(
        select(Product).where(Product.id == body.product_id).options(selectinload(Product.price_history))
    )
    if not product:
        raise HTTPException(404, "Product not found")

    existing = await db.scalar(select(Watchlist).where(Watchlist.product_id == body.product_id))
    if existing:
        raise HTTPException(409, "Product already in watchlist")

    current_price = product.price_history[-1].price if product.price_history else None
    w = Watchlist(
        product_id=body.product_id,
        alerta_pct=body.alerta_pct,
        precio_al_agregar=current_price,
    )
    db.add(w)
    await db.flush()
    return {"id": w.id, "product_id": w.product_id, "precio_al_agregar": current_price}


class WatchlistUpdate(BaseModel):
    alerta_pct: float = Field(ge=0, le=100)


@router.patch("/{watchlist_id}")
async def update_watchlist(watchlist_id: int, body: WatchlistUpdate, db: AsyncSession = Depends(get_db)):
    w = await db.scalar(select(Watchlist).where(Watchlist.id == watchlist_id))
    if not w:
        raise HTTPException(404, "Watchlist entry not found")
    w.alerta_pct = body.alerta_pct
    await db.flush()
    return {"id": w.id, "alerta_pct": w.alerta_pct}


@router.delete("/{watchlist_id}", status_code=204)
async def remove_from_watchlist(watchlist_id: int, db: AsyncSession = Depends(get_db)):
    w = await db.scalar(select(Watchlist).where(Watchlist.id == watchlist_id))
    if not w:
        raise HTTPException(404, "Watchlist entry not found")
    await db.delete(w)
