import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ExternalLink, Bookmark, BookmarkCheck, TrendingUp, TrendingDown, Minus, RefreshCw } from "lucide-react";
import PriceChart from "../components/PriceChart";
import { endpoints } from "../api/client";

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 text-center">
      <p className="text-slate-400 text-xs mb-1">{label}</p>
      <p className="text-white font-bold text-lg">{value}</p>
    </div>
  );
}

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const productId = Number(id);
  const qc = useQueryClient();

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

  const inWatchlist = watchlist.some((w) => w.product_id === productId);
  const watchlistEntry = watchlist.find((w) => w.product_id === productId);

  const addMutation = useMutation({
    mutationFn: () => endpoints.addToWatchlist(productId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlist"] }),
  });
  const removeMutation = useMutation({
    mutationFn: () => endpoints.removeFromWatchlist(watchlistEntry!.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlist"] }),
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
    </div>
  );
}
