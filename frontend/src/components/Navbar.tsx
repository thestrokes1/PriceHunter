import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search, Bookmark, LayoutDashboard, TrendingUp } from "lucide-react";

export default function Navbar() {
  const [q, setQ] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <TrendingUp className="text-blue-400" size={24} />
          <span className="text-white font-bold text-lg tracking-tight">
            Price<span className="text-blue-400">Hunter</span>
          </span>
        </Link>

        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <div className="relative flex-1 max-w-xl">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Buscar en MercadoLibre y Amazon..."
              className="w-full bg-slate-700 text-white placeholder-slate-400 rounded-lg pl-9 pr-4 py-2 text-sm border border-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Buscar
          </button>
        </form>

        <div className="flex items-center gap-1 shrink-0">
          <Link
            to="/watchlist"
            className="flex items-center gap-1.5 text-slate-300 hover:text-white px-3 py-2 rounded-lg hover:bg-slate-700 transition-colors text-sm"
          >
            <Bookmark size={16} />
            <span className="hidden sm:inline">Watchlist</span>
          </Link>
          <Link
            to="/admin"
            className="flex items-center gap-1.5 text-slate-300 hover:text-white px-3 py-2 rounded-lg hover:bg-slate-700 transition-colors text-sm"
          >
            <LayoutDashboard size={16} />
            <span className="hidden sm:inline">Admin</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}
