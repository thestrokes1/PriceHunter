# PriceHunter — Comparador de precios

Aplicación full stack para comparar y trackear precios en **MercadoLibre AR**, **Frávega** y **Amazon.com** de forma simultánea. Incluye historial de precios, watchlist personal con alertas configurables por email y comparación cross-plataforma.

**Demo:** [pricehunter-pied.vercel.app](https://pricehunter-pied.vercel.app) &nbsp;·&nbsp; **API:** [pricehunter-api.onrender.com/docs](https://pricehunter-api.onrender.com/docs)

---

## Screenshots

### Home — Categorías y búsquedas populares
![Home](docs/screenshots/home.png)

### Resultados — Grid ML + Amazon con filtros por fuente y sort por precio
![Search Results](docs/screenshots/search_results.png)

### Detalle — Historial 30 días + comparación cross-plataforma
![Product Detail](docs/screenshots/product_detail.png)

### Watchlist — Alertas configurables y semáforo de variación
![Watchlist](docs/screenshots/watchlist.png)

---

## Features

**Búsqueda y resultados**
- Búsqueda simultánea en MercadoLibre AR + Amazon.com, resultados en grid adaptativo
- Filtros por fuente (ML / Frávega / Amazon) — toggle individual, oculta columnas vacías
- Sort por precio asc/desc aplicado a todas las columnas al mismo tiempo
- 8 categorías con búsqueda directa (Tecnología, Celulares, Motos, Autos, etc.)

**Detalle de producto**
- Historial de precios con gráfico de área interactivo (Recharts), 30+ puntos
- Stats de precio: mínimo / promedio / máximo sobre el historial
- Widget de comparación cross-plataforma — muestra top 3 resultados del otro scraper
- Indicador de variación % respecto al precio inicial

**Watchlist y alertas**
- Watchlist personal — agregar/quitar con un click
- Alerta % configurable por producto — edición inline en la tabla
- **Alertas por email** — cuando el precio baja ≥ alerta_pct, llega un email HTML con badge de precio, % de bajada y link directo al producto
- Semáforo verde/rojo de variación en la tabla

**Sistema**
- Scraping automático cada 6h via APScheduler
- Toast notifications en todas las acciones de watchlist
- Paleta dark navy con badges por fuente (ML amarillo / Amazon naranja / Frávega azul)

---

## Tech Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + Python 3.11 |
| ORM | SQLAlchemy 2.0 async |
| Base de datos | PostgreSQL (Render) |
| Scraping ML | httpx + BeautifulSoup4 (poly-card selectors) |
| Scraping Amazon | curl_cffi `impersonate="chrome124"` — bypass TLS fingerprint |
| Scraping Frávega | Playwright + Apollo `__NEXT_DATA__` GraphQL JSON |
| Scheduler | APScheduler cada 6h |
| Email | smtplib + Gmail SMTP — templates HTML |
| Frontend | React 18 + Vite + TypeScript |
| Estilos | Tailwind CSS v3 |
| Gráficos | Recharts |
| HTTP client | TanStack Query + Axios |
| Deploy API | Render (Oregon) |
| Deploy Frontend | Vercel |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Vercel)                                       │
│  React 18 + TypeScript + TanStack Query + Tailwind      │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS REST
┌───────────────────────▼─────────────────────────────────┐
│  Backend API (Render — Oregon)                           │
│  FastAPI + SQLAlchemy async                              │
│                                                          │
│  GET /search ──► ml_scraper    (httpx + BS4)            │
│             ──► amazon_scraper (curl_cffi Chrome TLS)   │
│             ──► fravega_scraper (Playwright / proxy AR) │
│                                                          │
│  APScheduler 6h ──► scrape watchlist                    │
│                 ──► detectar drops ≥ alerta_pct         │
│                 ──► send_price_alert() → Gmail SMTP     │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  PostgreSQL (Render)                                     │
│  products · price_history · watchlist · categories       │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

```
GET  /health
GET  /categories

GET  /search?q=...&cat=slug&limit=10
     → { ml: [...], fravega: [...], amazon: [...] }

GET  /products/{id}
GET  /products/{id}/history
POST /products/{id}/scrape

GET    /watchlist
POST   /watchlist         { product_id, alerta_pct }
PATCH  /watchlist/{id}    { alerta_pct }
DELETE /watchlist/{id}

GET  /admin/products?source=&cat=
GET  /admin/stats
POST /admin/scrape-all
POST /admin/seed-history
```

---

## Setup local

### Backend

```bash
git clone https://github.com/thestrokes1/PriceHunter.git
cd PriceHunter

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
playwright install chromium       # para scraping Frávega local

# Configurar variables de entorno
cp .env.example .env
# Editar: DATABASE_URL, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

# Inicializar DB y 8 categorías
PYTHONPATH=. python backend/db/init_db.py

# Iniciar API
PYTHONPATH=. uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev   # → http://localhost:5173
```

---

## Variables de entorno

| Variable | Descripción |
|----------|------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `USE_PLAYWRIGHT` | `true` local (Amazon), `false` prod |
| `EMAIL_SENDER` | Gmail que envía las alertas |
| `EMAIL_PASSWORD` | App Password de Gmail (16 chars) |
| `EMAIL_RECEIVER` | Email que recibe las alertas |
| `FRAVEGA_PROXY` | Proxy AR opcional para Frávega en prod |
| `VITE_API_URL` | URL del backend (frontend) |

---

## Notas de scraping

| Fuente | Técnica | Estado prod |
|--------|---------|------------|
| MercadoLibre | httpx + BS4, selectores `poly-card` de Andes DS | ✅ |
| Amazon | curl_cffi con `impersonate="chrome124"` — bypass TLS fingerprint de Cloudflare | ✅ |
| Frávega | Playwright + parseo del cache Apollo GraphQL en `__NEXT_DATA__` | ⚠️ Geo-blocked en datacenter |

**Frávega:** Cloudflare detecta IPs de datacenter (Render Oregon). Funciona desde IP argentina. Para producción: proxy AR o GitHub Actions cron con IP de GitHub.

---

## Deploy

| Servicio | Plataforma | URL |
|---------|-----------|-----|
| Frontend | Vercel | [pricehunter-pied.vercel.app](https://pricehunter-pied.vercel.app) |
| Backend | Render free | [pricehunter-api.onrender.com](https://pricehunter-api.onrender.com) |
| Base de datos | Render PostgreSQL | Oregon, US |

> El free tier de Render duerme tras 15 min de inactividad — la primera request puede tardar ~15-20s.

---

Desarrollado por **Cristian Vázquez** — proyecto portfolio Full Stack Python + React.  
[github.com/thestrokes1](https://github.com/thestrokes1)
