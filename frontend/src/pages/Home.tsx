import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search, TrendingUp } from "lucide-react";
import { useState } from "react";
import { endpoints } from "../api/client";

export default function Home() {
  const [q, setQ] = useState("");
  const navigate = useNavigate();

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => endpoints.categories().then((r) => r.data),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  return (
    <div className="flex flex-col gap-12">
      {/* Hero */}
      <div className="text-center py-12">
        <div className="flex items-center justify-center gap-3 mb-4">
          <TrendingUp className="text-blue-400" size={40} />
          <h1 className="text-4xl font-bold text-white">
            Price<span className="text-blue-400">Hunter</span>
          </h1>
        </div>
        <p className="text-slate-400 text-lg mb-8">
          Compara precios en MercadoLibre y Amazon al mismo tiempo
        </p>
        <form onSubmit={handleSearch} className="max-w-xl mx-auto flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="¿Qué estás buscando?"
              className="w-full bg-slate-800 text-white placeholder-slate-400 rounded-xl pl-12 pr-4 py-3 text-base border border-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
          >
            Buscar
          </button>
        </form>
      </div>

      {/* Categories */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Categorías</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {categories.map((cat) => (
            <button
              key={cat.slug}
              onClick={() => navigate(`/search?q=${cat.nombre}&cat=${cat.slug}`)}
              className="bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-500 rounded-xl p-4 flex flex-col items-center gap-2 transition-all group"
            >
              <span className="text-3xl">{cat.icono}</span>
              <span
                className="text-sm font-medium"
                style={{ color: cat.color }}
              >
                {cat.nombre}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Popular searches */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4">Búsquedas populares</h2>
        <div className="flex flex-wrap gap-2">
          {["iPhone 15", "MacBook Air", "Samsung Galaxy", "AirPods", "PlayStation 5", "Notebook HP", "Arduino", "Monitor 4K"].map((term) => (
            <button
              key={term}
              onClick={() => navigate(`/search?q=${encodeURIComponent(term)}`)}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 px-4 py-2 rounded-full text-sm transition-colors"
            >
              {term}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
