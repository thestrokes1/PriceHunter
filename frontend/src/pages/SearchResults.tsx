import { useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertCircle } from "lucide-react";
import ProductCard from "../components/ProductCard";
import { endpoints } from "../api/client";

function SkeletonCard() {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 flex gap-4 animate-pulse">
      <div className="w-20 h-20 bg-slate-700 rounded-lg shrink-0" />
      <div className="flex-1 flex flex-col gap-2">
        <div className="h-4 bg-slate-700 rounded w-16" />
        <div className="h-4 bg-slate-700 rounded w-full" />
        <div className="h-4 bg-slate-700 rounded w-2/3" />
        <div className="h-5 bg-slate-700 rounded w-24 mt-auto" />
      </div>
    </div>
  );
}

export default function SearchResults() {
  const [params] = useSearchParams();
  const q = params.get("q") ?? "";
  const cat = params.get("cat") ?? undefined;
  const qc = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["search", q, cat],
    queryFn: () => endpoints.search(q, cat).then((r) => r.data),
    enabled: !!q,
  });

  const { data: watchlist = [] } = useQuery({
    queryKey: ["watchlist"],
    queryFn: () => endpoints.watchlist().then((r) => r.data),
  });

  const watchlistIds = new Set(watchlist.map((w) => w.product_id));

  const addMutation = useMutation({
    mutationFn: (id: number) => endpoints.addToWatchlist(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlist"] }),
  });
  const removeMutation = useMutation({
    mutationFn: async (product_id: number) => {
      const entry = watchlist.find((w) => w.product_id === product_id);
      if (entry) await endpoints.removeFromWatchlist(entry.id);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlist"] }),
  });

  const toggleWatchlist = (id: number) => {
    if (watchlistIds.has(id)) removeMutation.mutate(id);
    else addMutation.mutate(id);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">
        Resultados para <span className="text-blue-400">"{q}"</span>
      </h1>

      {isError && (
        <div className="flex items-center gap-2 text-red-400 bg-red-400/10 border border-red-400/30 rounded-lg p-4 mb-6">
          <AlertCircle size={18} />
          <span>Error al buscar. Verifica que el backend esté corriendo.</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* MercadoLibre column */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-bold px-2 py-1 rounded-full bg-yellow-500 text-yellow-900">MercadoLibre</span>
            {!isLoading && <span className="text-slate-500 text-sm">{data?.ml.length ?? 0} resultados</span>}
          </div>
          <div className="flex flex-col gap-3">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
            ) : data?.ml.length === 0 ? (
              <p className="text-slate-500 text-sm py-8 text-center">Sin resultados en MercadoLibre</p>
            ) : (
              data?.ml.map((p) => (
                <ProductCard
                  key={p.id}
                  product={p}
                  inWatchlist={watchlistIds.has(p.id)}
                  onToggleWatchlist={toggleWatchlist}
                />
              ))
            )}
          </div>
        </div>

        {/* Amazon column */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-bold px-2 py-1 rounded-full bg-orange-500 text-orange-900">Amazon</span>
            {!isLoading && <span className="text-slate-500 text-sm">{data?.amazon.length ?? 0} resultados</span>}
          </div>
          <div className="flex flex-col gap-3">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
            ) : data?.amazon.length === 0 ? (
              <p className="text-slate-500 text-sm py-8 text-center">Sin resultados en Amazon</p>
            ) : (
              data?.amazon.map((p) => (
                <ProductCard
                  key={p.id}
                  product={p}
                  inWatchlist={watchlistIds.has(p.id)}
                  onToggleWatchlist={toggleWatchlist}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
