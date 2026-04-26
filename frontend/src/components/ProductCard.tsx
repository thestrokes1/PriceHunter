import { Link } from "react-router-dom";
import { Star, Bookmark, BookmarkCheck, ExternalLink } from "lucide-react";
import type { ProductResult } from "../api/client";

interface Props {
  product: ProductResult;
  inWatchlist?: boolean;
  onToggleWatchlist?: (id: number) => void;
}

const SOURCE_STYLES: Record<string, { label: string; bg: string; text: string }> = {
  mercadolibre: { label: "MercadoLibre", bg: "bg-yellow-500", text: "text-yellow-900" },
  amazon:        { label: "Amazon",       bg: "bg-orange-500", text: "text-orange-900" },
  fravega:       { label: "Frávega",      bg: "bg-blue-500",   text: "text-blue-50"   },
};

export default function ProductCard({ product, inWatchlist, onToggleWatchlist }: Props) {
  const src = SOURCE_STYLES[product.source] ?? { label: product.source, bg: "bg-slate-600", text: "text-white" };
  const price = product.currency === "ARS"
    ? `$${product.price.toLocaleString("es-AR")}`
    : `USD ${product.price.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 flex gap-4 hover:border-slate-500 transition-colors group">
      <Link to={`/product/${product.id}`} className="shrink-0">
        {product.imagen_url ? (
          <img
            src={product.imagen_url}
            alt={product.title}
            className="w-20 h-20 object-contain rounded-lg bg-white p-1"
            onError={(e) => { (e.target as HTMLImageElement).src = "/placeholder.svg"; }}
          />
        ) : (
          <div className="w-20 h-20 bg-slate-700 rounded-lg flex items-center justify-center text-slate-500 text-2xl">
            📦
          </div>
        )}
      </Link>

      <div className="flex-1 min-w-0 flex flex-col gap-1">
        <div className="flex items-start justify-between gap-2">
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${src.bg} ${src.text} shrink-0`}>
            {src.label}
          </span>
          <div className="flex items-center gap-1">
            <a href={product.url} target="_blank" rel="noopener noreferrer"
              className="text-slate-500 hover:text-slate-300 transition-colors">
              <ExternalLink size={14} />
            </a>
            {onToggleWatchlist && (
              <button
                onClick={() => onToggleWatchlist(product.id)}
                className="text-slate-500 hover:text-blue-400 transition-colors"
                title={inWatchlist ? "Quitar de watchlist" : "Agregar a watchlist"}
              >
                {inWatchlist ? <BookmarkCheck size={16} className="text-blue-400" /> : <Bookmark size={16} />}
              </button>
            )}
          </div>
        </div>

        <Link to={`/product/${product.id}`}>
          <p className="text-white text-sm leading-tight line-clamp-2 group-hover:text-blue-300 transition-colors">
            {product.title}
          </p>
        </Link>

        <div className="flex items-center justify-between mt-auto">
          <span className="text-blue-400 font-bold text-base">{price}</span>
          {product.rating && (
            <span className="flex items-center gap-1 text-slate-400 text-xs">
              <Star size={12} className="text-yellow-400 fill-yellow-400" />
              {product.rating.toFixed(1)}
              {product.reviews && <span className="text-slate-500">({product.reviews.toLocaleString()})</span>}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
