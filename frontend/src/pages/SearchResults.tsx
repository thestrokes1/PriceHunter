import { useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertCircle } from "lucide-react";
import ProductCard from "../components/ProductCard";
import { endpoints } from "../api/client";
import type { ProductResult } from "../api/client";

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

interface ColumnProps {
  label: string;
  badgeBg: string;
  badgeText: string;
  products: ProductResult[];
  isLoading: boolean;
  watchlistIds: Set<number>;
  onToggle: (id: number) => void;
  emptyMsg: string;
}

function ResultColumn({ label, badgeBg, badgeText, products, isLoading, watchlistIds, onToggle, emptyMsg }: ColumnProps) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span className={`text-xs font-bold px-2 py-1 rounded-full ${badgeBg} ${badgeText}`}>{label}</span>
        {!isLoading && <span className="text-slate-500 text-sm">{products.length} resultados</span>}
      </div>
      <div className="flex flex-col gap-3">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : products.length === 0 ? (
          <p className="text-slate-500 text-sm py-8 text-center">{emptyMsg}</p>
        ) : (
          products.map((p) => (
            <ProductCard
              key={p.id}
              product={p}
              inWatchlist={watchlistIds.has(p.id)}
              onToggleWatchlist={onToggle}
            />
          ))
        )}
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

  const allColumns = [
    {
      key: "ml",
      label: "MercadoLibre",
      badgeBg: "bg-yellow-500",
      badgeText: "text-yellow-900",
      products: data?.ml ?? [],
      emptyMsg: "Sin resultados en MercadoLibre",
    },
    {
      key: "fravega",
      label: "Frávega",
      badgeBg: "bg-blue-500",
      badgeText: "text-blue-50",
      products: data?.fravega ?? [],
      emptyMsg: "Sin resultados en Frávega",
    },
    {
      key: "amazon",
      label: "Amazon",
      badgeBg: "bg-orange-500",
      badgeText: "text-orange-900",
      products: data?.amazon ?? [],
      emptyMsg: "Sin resultados en Amazon",
    },
  ];

  // While loading show all 3 columns (skeletons). Once loaded, hide sources with 0 results.
  const columns = isLoading
    ? allColumns
    : allColumns.filter((col) => col.products.length > 0);

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

      <div className={`grid grid-cols-1 gap-6 ${columns.length === 1 ? "max-w-xl" : columns.length === 2 ? "lg:grid-cols-2" : "lg:grid-cols-3"}`}>
        {columns.map((col) => (
          <ResultColumn
            key={col.key}
            label={col.label}
            badgeBg={col.badgeBg}
            badgeText={col.badgeText}
            products={col.products}
            isLoading={isLoading}
            watchlistIds={watchlistIds}
            onToggle={toggleWatchlist}
            emptyMsg={col.emptyMsg}
          />
        ))}
      </div>
    </div>
  );
}
