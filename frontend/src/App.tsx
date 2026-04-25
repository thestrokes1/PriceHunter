import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import SearchResults from "./pages/SearchResults";
import ProductDetail from "./pages/ProductDetail";
import Watchlist from "./pages/Watchlist";
import Admin from "./pages/Admin";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-900">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </main>
    </div>
  );
}
