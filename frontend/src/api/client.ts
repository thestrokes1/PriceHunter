import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BASE_URL });

// Types
export interface Category {
  id: number;
  nombre: string;
  slug: string;
  icono: string;
  color: string;
}

export interface ProductResult {
  id: number;
  title: string;
  url: string;
  source: "mercadolibre" | "amazon";
  price: number;
  currency: string;
  imagen_url: string | null;
  rating: number | null;
  reviews: number | null;
}

export interface ProductDetail {
  id: number;
  title: string;
  url: string;
  source: "mercadolibre" | "amazon";
  imagen_url: string | null;
  rating: number | null;
  reviews: number | null;
  current_price: number | null;
  currency: string | null;
  price_change_pct: number | null;
  min_price: number | null;
  max_price: number | null;
  avg_price: number | null;
  created_at: string;
}

export interface PricePoint {
  price: number;
  currency: string;
  scraped_at: string;
}

export interface WatchlistItem {
  id: number;
  product_id: number;
  title: string;
  url: string;
  source: string;
  imagen_url: string | null;
  currency: string | null;
  precio_al_agregar: number | null;
  current_price: number | null;
  change_pct: number | null;
  alerta_pct: number;
  added_at: string;
}

export interface AdminProduct {
  id: number;
  title: string;
  url: string;
  source: string;
  category: string | null;
  current_price: number | null;
  currency: string | null;
  price_count: number;
  imagen_url: string | null;
  created_at: string;
}

export interface AdminStats {
  total_products: number;
  mercadolibre_products: number;
  amazon_products: number;
  watchlist_items: number;
  total_price_records: number;
  last_scrape: string | null;
}

// Endpoints
export const endpoints = {
  health: () => api.get("/health"),
  categories: () => api.get<Category[]>("/categories"),
  search: (q: string, cat?: string, limit = 10) =>
    api.get<{ query: string; ml: ProductResult[]; amazon: ProductResult[] }>("/search", {
      params: { q, cat, limit },
    }),
  product: (id: number) => api.get<ProductDetail>(`/products/${id}`),
  history: (id: number) => api.get<PricePoint[]>(`/products/${id}/history`),
  scrapeProduct: (id: number) => api.post(`/products/${id}/scrape`),
  watchlist: () => api.get<WatchlistItem[]>("/watchlist"),
  addToWatchlist: (product_id: number, alerta_pct = 5) =>
    api.post("/watchlist", { product_id, alerta_pct }),
  removeFromWatchlist: (id: number) => api.delete(`/watchlist/${id}`),
  adminProducts: (source?: string, cat?: string) =>
    api.get<AdminProduct[]>("/admin/products", { params: { source, cat } }),
  adminStats: () => api.get<AdminStats>("/admin/stats"),
  scrapeAll: () => api.post("/admin/scrape-all"),
};
