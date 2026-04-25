import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Trash2, TrendingUp, TrendingDown, Minus, ExternalLink } from "lucide-react";
import { endpoints } from "../api/client";

export default function Watchlist() {
  const qc = useQueryClient();

  const { data: watchlist = [], isLoading } = useQuery({
    queryKey: ["watchlist"],
    queryFn: () => endpoints.watchlist().then((r) => r.data),
  });

  const removeMutation = useMutation({
    mutationFn: (id: number) => endpoints.removeFromWatchlist(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlist"] }),
  });

  const formatPrice = (v: number | null, currency: string | null) => {
    if (v == null) return "—";
    return currency === "ARS"
      ? `$${v.toLocaleString("es-AR")}`
      : `USD ${v.toFixed(2)}`;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Mi Watchlist</h1>
        <span className="text-slate-400 text-sm">{watchlist.length} productos</span>
      </div>

      {isLoading && (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {!isLoading && watchlist.length === 0 && (
        <div className="text-center py-16 text-slate-500">
          <p className="text-4xl mb-4">🔖</p>
          <p>Tu watchlist está vacía.</p>
          <p className="text-sm mt-1">Buscá productos y agregaos con el botón de marcar.</p>
        </div>
      )}

      {watchlist.length > 0 && (
        <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-900/50">
              <tr className="text-slate-400 text-xs uppercase tracking-wide">
                <th className="text-left px-4 py-3">Producto</th>
                <th className="text-right px-4 py-3 hidden sm:table-cell">Al agregar</th>
                <th className="text-right px-4 py-3">Actual</th>
                <th className="text-right px-4 py-3">Variación</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {watchlist.map((item) => {
                const pct = item.change_pct;
                return (
                  <tr key={item.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        {item.imagen_url && (
                          <img src={item.imagen_url} alt="" className="w-10 h-10 object-contain rounded bg-white p-0.5 shrink-0" />
                        )}
                        <div className="min-w-0">
                          <Link to={`/product/${item.product_id}`} className="text-white text-sm hover:text-blue-300 line-clamp-1">
                            {item.title}
                          </Link>
                          <div className="flex items-center gap-2">
                            <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold mt-0.5 ${
                              item.source === "mercadolibre"
                                ? "bg-yellow-500 text-yellow-900"
                                : "bg-orange-500 text-orange-900"
                            }`}>
                              {item.source === "mercadolibre" ? "ML" : "AMZ"}
                            </span>
                            <a href={item.url} target="_blank" rel="noopener noreferrer"
                              className="text-slate-500 hover:text-slate-300">
                              <ExternalLink size={12} />
                            </a>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right text-slate-400 text-sm hidden sm:table-cell">
                      {formatPrice(item.precio_al_agregar, item.currency)}
                    </td>
                    <td className="px-4 py-3 text-right text-blue-400 font-medium text-sm">
                      {formatPrice(item.current_price, item.currency)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {pct == null ? (
                        <span className="text-slate-500 text-sm">—</span>
                      ) : (
                        <span className={`flex items-center justify-end gap-1 text-sm font-medium ${
                          pct < 0 ? "text-green-400" : pct > 0 ? "text-red-400" : "text-slate-400"
                        }`}>
                          {pct < 0 ? <TrendingDown size={14} /> : pct > 0 ? <TrendingUp size={14} /> : <Minus size={14} />}
                          {pct > 0 ? "+" : ""}{pct.toFixed(1)}%
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => removeMutation.mutate(item.id)}
                        className="text-slate-500 hover:text-red-400 transition-colors"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
