import { useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { useState, useEffect } from "react";
import ProductCard from "../components/ProductCard";
import { endpoints } from "../api/client";
import type { ProductResult } from "../api/client";

// ── Toast ──────────────────────────────────────────────────────────────────
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

// ── Skeleton ───────────────────────────────────────────────────────────────
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

// ── Column ─────────────────────────────────────────────────────────────────
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

// ── Main ───────────────────────────────────────────────────────────────────
type SortOrder = "asc" | "desc" | null;

export default function SearchResults() {
  const [params] = useSearchParams();
  const q = params.get("q") ?? "";
  const cat = params.get("cat") ?? undefined;
  const qc = useQueryClient();

  const [sortOrder, setSortOrder] = useState<SortOrder>(null);
  const [activeSources, setActiveSources] = useState<Set<string>>(new Set(["ml", "fravega", "amazon"]));
  const [toast, setToast] = useState<ToastState | null>(null);

  const showToast = (msg: string, type: ToastState["type"] = "success") => {
    setToast({ msg, type });
  };

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(t);
  }, [toast]);

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
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["watchlist"] });
      showToast("Agregado a watchlist ✓", "success");
    },
  });

  const removeMutation = useMutation({
    mutationFn: async (product_id: number) => {
      const entry = watchlist.find((w) => w.product_id === product_id);
      if (entry) await endpoints.removeFromWatchlist(entry.id);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["watchlist"] });
      showToast("Eliminado de watchlist", "error");
    },
  });

  const toggleWatchlist = (id: number) => {
    if (watchlistIds.has(id)) removeMutation.mutate(id);
    else addMutation.mutate(id);
  };

  const sortProducts = (products: ProductResult[]) => {
    if (!sortOrder) return products;
    return [...products].sort((a, b) =>
      sortOrder === "asc" ? a.price - b.price : b.price - a.price
    );
  };

  const cycleSortOrder = () => {
    setSortOrder((prev) => (prev === null ? "asc" : prev === "asc" ? "desc" : null));
  };

  const toggleSource = (key: string) => {
    setActiveSources((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const allColumns = [
    {
      key: "ml",
      label: "MercadoLibre",
      badgeBg: "bg-yellow-500",
      badgeText: "text-yellow-900",
      products: sortProducts(data?.ml ?? []),
      emptyMsg: "Sin resultados en MercadoLibre",
    },
    {
      key: "fravega",
      label: "Frávega",
      badgeBg: "bg-blue-500",
      badgeText: "text-blue-50",
      products: sortProducts(data?.fravega ?? []),
      emptyMsg: "Sin resultados en Frávega",
    },
    {
      key: "amazon",
      label: "Amazon",
      badgeBg: "bg-orange-500",
      badgeText: "text-orange-900",
      products: sortProducts(data?.amazon ?? []),
      emptyMsg: "Sin resultados en Amazon",
    },
  ];

  // Sources that actually have results (used for filter toggles)
  const availableSources = isLoading
    ? allColumns.map((c) => c.key)
    : allColumns.filter((c) => c.products.length > 0).map((c) => c.key);

  const columns = isLoading
    ? allColumns
    : allColumns.filter((col) => col.products.length > 0 && activeSources.has(col.key));

  const gridClass =
    columns.length === 1
      ? "max-w-xl"
      : columns.length === 2
      ? "md:grid-cols-2"
      : "lg:grid-cols-3";

  const SortIcon = sortOrder === "asc" ? ArrowUp : sortOrder === "desc" ? ArrowDown : ArrowUpDown;
  const sortLabel = sortOrder === "asc" ? "Precio ↑" : sortOrder === "desc" ? "Precio ↓" : "Ordenar";

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <h1 className="text-2xl font-bold text-white">
          Resultados para <span className="text-blue-400">"{q}"</span>
        </h1>

        <div className="flex flex-wrap items-center gap-2">
          {/* Source filter toggles */}
          {!isLoading && availableSources.length > 1 && allColumns
            .filter((c) => availableSources.includes(c.key))
            .map((col) => (
              <button
                key={col.key}
                onClick={() => toggleSource(col.key)}
                className={`text-xs font-bold px-3 py-1.5 rounded-full border transition-all ${
                  activeSources.has(col.key)
                    ? `${col.badgeBg} ${col.badgeText} border-transparent`
                    : "bg-transparent border-slate-600 text-slate-400 hover:border-slate-400"
                }`}
              >
                {col.label}
              </button>
            ))}

          {/* Sort button */}
          <button
            onClick={cycleSortOrder}
            className={`flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-full border transition-all ${
              sortOrder
                ? "bg-blue-600 text-white border-transparent"
                : "bg-transparent border-slate-600 text-slate-400 hover:border-slate-400 hover:text-slate-300"
            }`}
          >
            <SortIcon size={14} />
            {sortLabel}
          </button>
        </div>
      </div>

      {isError && (
        <div className="flex items-center gap-2 text-red-400 bg-red-400/10 border border-red-400/30 rounded-lg p-4 mb-6">
          <AlertCircle size={18} />
          <span>Error al buscar. Verifica que el backend esté corriendo.</span>
        </div>
      )}

      <div className={`grid grid-cols-1 gap-6 ${gridClass}`}>
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

      <Toast toast={toast} />
    </div>
  );
}
