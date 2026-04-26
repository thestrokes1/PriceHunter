import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Package, Star, Database, Clock, ChevronLeft, ChevronRight } from "lucide-react";
import { endpoints } from "../api/client";

const PAGE_SIZE = 20;

const SOURCE_BADGE: Record<string, { label: string; bg: string; text: string }> = {
  mercadolibre: { label: "MercadoLibre", bg: "bg-yellow-500", text: "text-yellow-900" },
  amazon:        { label: "Amazon",       bg: "bg-orange-500", text: "text-orange-900" },
  fravega:       { label: "Frávega",      bg: "bg-blue-500",   text: "text-blue-50"   },
};

function StatBox({ icon: Icon, label, value, color }: { icon: any; label: string; value: number | string; color: string }) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 flex items-center gap-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-slate-400 text-xs">{label}</p>
        <p className="text-white font-bold text-xl">{value}</p>
      </div>
    </div>
  );
}

export default function Admin() {
  const qc = useQueryClient();
  const [page, setPage] = useState(0);
  const [sourceFilter, setSourceFilter] = useState<string>("all");

  const { data: stats } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => endpoints.adminStats().then((r) => r.data),
  });

  const { data: allProducts = [], isLoading } = useQuery({
    queryKey: ["admin-products"],
    queryFn: () => endpoints.adminProducts().then((r) => r.data),
  });

  const scrapeAllMutation = useMutation({
    mutationFn: () => endpoints.scrapeAll(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-stats"] });
      qc.invalidateQueries({ queryKey: ["admin-products"] });
    },
  });

  const filtered = sourceFilter === "all"
    ? allProducts
    : allProducts.filter((p) => p.source === sourceFilter);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const products = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const handleFilter = (src: string) => {
    setSourceFilter(src);
    setPage(0);
  };

  const formatDate = (iso: string | null) =>
    iso ? new Date(iso).toLocaleString("es-AR") : "Nunca";

  const formatPrice = (v: number | null, currency: string | null) => {
    if (v == null) return "—";
    return currency === "ARS"
      ? `$${v.toLocaleString("es-AR")}`
      : `USD ${v.toFixed(2)}`;
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Panel de Control</h1>
        <button
          onClick={() => scrapeAllMutation.mutate()}
          disabled={scrapeAllMutation.isPending}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <RefreshCw size={16} className={scrapeAllMutation.isPending ? "animate-spin" : ""} />
          {scrapeAllMutation.isPending ? "Scrapeando..." : "Scrapear todo"}
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatBox icon={Package} label="Total productos" value={stats.total_products} color="bg-blue-600" />
          <StatBox icon={Star} label="Watchlist items" value={stats.watchlist_items} color="bg-purple-600" />
          <StatBox icon={Database} label="Registros de precio" value={stats.total_price_records} color="bg-green-600" />
          <StatBox icon={Clock} label="Último scrape" value={formatDate(stats.last_scrape)} color="bg-orange-600" />
        </div>
      )}

      {scrapeAllMutation.isSuccess && (
        <div className="bg-green-500/10 border border-green-500/30 text-green-400 rounded-lg px-4 py-3 text-sm">
          Scraping completado: {(scrapeAllMutation.data as any)?.data?.scraped ?? 0} actualizados,{" "}
          {(scrapeAllMutation.data as any)?.data?.errors ?? 0} errores.
        </div>
      )}

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700 flex flex-wrap items-center gap-3 justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-white font-semibold">Productos en seguimiento</h2>
            <span className="text-slate-400 text-sm">{filtered.length} total</span>
          </div>
          <div className="flex gap-1">
            {["all", "mercadolibre", "fravega", "amazon"].map((src) => (
              <button
                key={src}
                onClick={() => handleFilter(src)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  sourceFilter === src
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                }`}
              >
                {src === "all" ? "Todos" : src === "mercadolibre" ? "MercadoLibre" : src === "fravega" ? "Frávega" : "Amazon"}
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            <table className="w-full">
              <thead className="bg-slate-900/50">
                <tr className="text-slate-400 text-xs uppercase tracking-wide">
                  <th className="text-left px-4 py-3">Producto</th>
                  <th className="text-left px-4 py-3 hidden md:table-cell">Fuente</th>
                  <th className="text-right px-4 py-3">Precio</th>
                  <th className="text-right px-4 py-3 hidden sm:table-cell">Registros</th>
                  <th className="text-right px-4 py-3 hidden lg:table-cell">Agregado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {products.map((p) => {
                  const badge = SOURCE_BADGE[p.source] ?? { label: p.source, bg: "bg-slate-600", text: "text-white" };
                  return (
                    <tr key={p.id} className="hover:bg-slate-700/30 transition-colors">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          {p.imagen_url && (
                            <img src={p.imagen_url} alt="" className="w-8 h-8 object-contain rounded bg-white p-0.5 shrink-0" />
                          )}
                          <a href={p.url} target="_blank" rel="noopener noreferrer"
                            className="text-white text-sm hover:text-blue-300 line-clamp-1 max-w-xs">
                            {p.title}
                          </a>
                        </div>
                      </td>
                      <td className="px-4 py-3 hidden md:table-cell">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${badge.bg} ${badge.text}`}>
                          {badge.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-blue-400 font-medium text-sm">
                        {formatPrice(p.current_price, p.currency)}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-400 text-sm hidden sm:table-cell">
                        {p.price_count}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-500 text-xs hidden lg:table-cell">
                        {new Date(p.created_at).toLocaleDateString("es-AR")}
                      </td>
                    </tr>
                  );
                })}
                {products.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-12 text-center text-slate-500">
                      No hay productos en seguimiento todavía.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            {totalPages > 1 && (
              <div className="px-4 py-3 border-t border-slate-700 flex items-center justify-between">
                <span className="text-slate-400 text-sm">
                  Página {page + 1} de {totalPages}
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => p - 1)}
                    disabled={page === 0}
                    className="p-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page >= totalPages - 1}
                    className="p-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
