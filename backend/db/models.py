from datetime import datetime
from sqlalchemy import Integer, Text, Float, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    icono: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str | None] = mapped_column(Text)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)  # 'mercadolibre' | 'amazon'
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    imagen_url: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[float | None] = mapped_column(Float)
    reviews: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    category: Mapped["Category | None"] = relationship(back_populates="products")
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="PriceHistory.scraped_at"
    )
    watchlist_entry: Mapped["Watchlist | None"] = relationship(back_populates="product", cascade="all, delete-orphan")

    @property
    def current_price(self) -> float | None:
        if self.price_history:
            return self.price_history[-1].price
        return None


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(Text, default="USD")
    scraped_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="price_history")


class Watchlist(Base):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    alerta_pct: Mapped[float] = mapped_column(Float, default=5.0)
    precio_al_agregar: Mapped[float | None] = mapped_column(Float)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("product_id"),)

    product: Mapped["Product"] = relationship(back_populates="watchlist_entry")
