import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ExternalLink, Bookmark, BookmarkCheck, TrendingUp, TrendingDown, Minus, RefreshCw } from "lucide-react";
import { useState, useEffect } from "react";
import PriceChart from "../components/PriceChart";
import { endpoints } from "../api/client";
import type { ProductResult } from "../api/client";

interface ToastState { msg: string; type: "success" | "error" }

function Toast({ toast }: { toast: ToastState | null }) {
  if (!toast) return null;
  return (
    <div className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium animate-fade-in
      ${toast.type === "success" ? "bg-green-600" : "bg-red-500"}`}>
      {toast.msg}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 text-center">
      <p className="text-slate-400 text-xs mb-1">{label}</p>
      <p className="text-white font-bold text-lg">{value}</p>
    </div>
  );
}

function CompareCard({ item }: { item: ProductResult }) {
  const isAmazon = item.source === "amazon";
  const priceStr = item.currency === "ARS"
    ? `$${item.price.toLocaleString("es-AR")}`
    : `USD ${item.price.toFixed(2)}`;

  return (
    <Link to={`/product/${item.id}`}
      className="flex items-center gap-3 bg-slate-900/60 hover:bg-slate-700/60 border border-slate-700 hover:border-slate-500 rounded-xl p-3 transition-all group">
      {item.imagen_url && (
        <img src={item.imagen_url} alt="" className="w-12 h-12 object-contain rounded-lg bg-white p-1 shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-white text-sm line-clamp-2 leading-tight group-hover:text-blue-300 transition-colors">
          {item.title}
        </p>
        {item.rating && (
          <p className="text-slate-500 text-xs mt-0.5">★ {item.rating}</p>
        )}
      </div>
      <div className="text-right shrink-0">
        <p className={`font-bold text-sm ${isAmazon ? "text-orange-400" : "text-yellow-400"}`}>
          {priceStr}
        </p>
      </div>
    </Link>
  );
}

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const productId = Number(id);
  const qc = useQueryClient();

  const [toast, setToast] = useState<ToastState | null>(null);
  const showToast = (msg: string, type: ToastState["type"] = "success") => setToast({ msg, type });

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(t);
  }, [toast]);

  const { data: product, isLoading } = useQuery({
    queryKey: ["product", productId],
    queryFn: () => endpoints.product(productId).then((r) => r.data),
  });

  const { data: history = [] } = useQuery({
    queryKey: ["history", productId],
    queryFn: () => endpoints.history(productId).then((r) => r.data),
  });

  const { data: watchlist = [] } = useQuery({
    queryKey: ["watchlist"],
    queryFn: () => endpoints.watchlist().then((r) => r.data),
  });

  // Comparison search on the other platform
  const { data: compareData } = useQuery({
    queryKey: ["compare", productId, product?.title],
    queryFn: () => endpoints.search(product!.title, undefined, 4).then((r) => r.data),
    enabled: !!product,
    staleTime: 1000 * 60 * 10,
  });

  const otherKey = product?.source === "mercadolibre" ? "amazon" : "ml";
  const otherLabel = product?.source === "mercadolibre" ? "Amazon" : "MercadoLibre";
  const otherBadge = product?.source === "mercadolibre"
    ? "bg-orange-500 text-orange-900"
    : "bg-yellow-500 text-yellow-900";
  const compareResults: ProductResult[] = (compareData?.[otherKey] ?? []).slice(0, 3);

  const inWatchlist = watchlist.some((w) => w.product_id === productId);
  const watchlistEntry = watchlist.find((w) => w.product_id === productId);

  const addMutation = useMutation({
    mutationFn: () => endpoints.addToWatchlist(productId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["watchlist"] });
      showToast("Agregado a watchlist ✓", "success");
    },
  });
  const removeMutation = useMutation({
    mutationFn: () => endpoints.removeFromWatchlist(watchlistEntry!.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["watchlist"] });
      showToast("Eliminado de watchlist", "error");
    },
  });
  const scrapeMutation = useMutation({
    mutationFn: () => endpoints.scrapeProduct(productId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["product", productId] });
      qc.invalidateQueries({ queryKey: ["history", productId] });
    },
  });

  if (isLoading) return (
    <div className="flex items-center justify-center py-24">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!product) return <p className="text-slate-400 text-center py-24">Producto no encontrado.</p>;

  const pct = product.price_change_pct;
  const currency = product.currency ?? "USD";
  const formatPrice = (v: number | null) =>
    v == null ? "—" : currency === "ARS"
      ? `$${v.toLocaleString("es-AR")}`
      : `USD ${v.toFixed(2)}`;

  return (
    <div className="flex flex-col gap-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 flex gap-6">
        {product.imagen_url && (
          <img src={product.imagen_url} alt={product.title}
            className="w-28 h-28 object-contain rounded-xl bg-white p-2 shrink-0" />
        )}
        <div className="flex-1 flex flex-col gap-2">
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full w-fit ${
            product.source === "mercadolibre"
              ? "bg-yellow-500 text-yellow-900"
              : "bg-orange-500 text-orange-900"
          }`}>
            {product.source === "mercadolibre" ? "MercadoLibre" : "Amazon"}
          </span>
          <h1 className="text-white font-semibold text-lg leading-tight">{product.title}</h1>
          <div className="flex items-center gap-3">
            <span className="text-blue-400 font-bold text-2xl">{formatPrice(product.current_price)}</span>
            {pct != null && (
              <span className={`flex items-center gap-1 text-sm font-medium ${
                pct < 0 ? "text-green-400" : pct > 0 ? "text-red-400" : "text-slate-400"
              }`}>
                {pct < 0 ? <TrendingDown size={16} /> : pct > 0 ? <TrendingUp size={16} /> : <Minus size={16} />}
                {pct > 0 ? "+" : ""}{pct.toFixed(1)}%
              </span>
            )}
          </div>
          <div className="flex gap-2 mt-2">
            <a href={product.url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1.5 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm transition-colors">
              <ExternalLink size={14} /> Ver en {product.source === "mercadolibre" ? "ML" : "Amazon"}
            </a>
            <button
              onClick={() => inWatchlist ? removeMutation.mutate() : addMutation.mutate()}
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              {inWatchlist ? <BookmarkCheck size={14} /> : <Bookmark size={14} />}
              {inWatchlist ? "En watchlist" : "Agregar"}
            </button>
            <button
              onClick={() => scrapeMutation.mutate()}
              disabled={scrapeMutation.isPending}
              className="flex items-center gap-1.5 bg-slate-700 hover:bg-slate-600 text-white px-3 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              <RefreshCw size={14} className={scrapeMutation.isPending ? "animate-spin" : ""} />
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <StatCard label="Precio mínimo" value={formatPrice(product.min_price)} />
        <StatCard label="Precio promedio" value={formatPrice(product.avg_price)} />
        <StatCard label="Precio máximo" value={formatPrice(product.max_price)} />
      </div>

      {/* Chart */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-5">
        <h2 className="text-white font-semibold mb-4">Historial de precios</h2>
        <PriceChart data={history} currency={currency} />
      </div>

      {/* Comparison widget */}
      {compareResults.length > 0 && (
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-5">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-white font-semibold">También en</h2>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${otherBadge}`}>
              {otherLabel}
            </span>
          </div>
          <div className="flex flex-col gap-2">
            {compareResults.map((item) => (
              <CompareCard key={item.id} item={item} />
            ))}
          </div>
          <Link
            to={`/search?q=${encodeURIComponent(product.title)}`}
            className="block text-center text-blue-400 hover:text-blue-300 text-sm mt-3 transition-colors"
          >
            Ver todos los resultados →
          </Link>
        </div>
      )}

      <Toast toast={toast} />
    </div>
  );
}
