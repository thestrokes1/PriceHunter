# PRICEHUNTER — CLAUDE.md
> Leer esto PRIMERO en cada sesión. Estado real y plan de mejoras.

---

## PROYECTO
Comparador y tracker de precios multi-plataforma.
Busca productos en **MercadoLibre AR**, **Frávega** y **Amazon.com** simultáneamente,
guarda historial de precios, permite armar una watchlist personal y tiene panel de control.
**Objetivo:** Portfolio laboral de Cristian — proyecto flagship completo y profesional.

## DUEÑO
Cristian — Python, JS/TS, Android (Kotlin), iOS, Java.
No hace nada manualmente — Claude ejecuta todo en terminal.
Claude controla Chrome con Playwright headless para tests visuales.

## DIRECTORIO RAÍZ
```
D:\Pricehunter
```

---

## URLS DE PRODUCCIÓN
| Servicio | URL |
|---|---|
| Frontend | https://pricehunter-pied.vercel.app |
| Backend API | https://pricehunter-api.onrender.com |
| Health check | https://pricehunter-api.onrender.com/health |

---

## STACK

| Capa | Herramienta |
|---|---|
| Backend | FastAPI + Python 3.11 (Render, Oregon) |
| ORM | SQLAlchemy 2.0 async |
| DB | PostgreSQL en Render (`dpg-d7mdrc9f9bms73fv2h7g-a`, expira 2026-05-25) |
| Scraping | httpx + BeautifulSoup4 + Playwright (solo local) |
| Scheduler | APScheduler cada 6h |
| Frontend | React 18 + Vite + TypeScript + Tailwind v3 |
| Gráficos | Recharts |
| HTTP client | TanStack Query + axios |
| Deploy API | Render (`srv-d7mjgju8bjmc738cpsd0`) |
| Deploy Frontend | Vercel |
| Entorno Python | venv en `D:\Pricehunter\venv` |

---

## ESTRUCTURA DE CARPETAS
```
D:\Pricehunter
├── CLAUDE.md / STATUS.md / README.md
├── .env                             ← secretos (nunca en git)
├── render.yaml
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── db/
│   │   ├── database.py              ← engine SQLAlchemy, get_db
│   │   ├── models.py                ← tablas: products, price_history, watchlist, categories
│   │   └── init_db.py               ← crear tablas + seed 8 categorías
│   ├── scrapers/
│   │   ├── ml_scraper.py            ← MercadoLibre AR (httpx, poly-card)
│   │   ├── amazon_scraper.py        ← Amazon.com (Playwright local / httpx prod)
│   │   ├── fravega_scraper.py       ← Frávega (Playwright local, vacío en prod)
│   │   └── utils.py                 ← headers, delays, truncate, clean_price
│   ├── routers/
│   │   ├── search.py                ← GET /search → {ml, fravega, amazon}
│   │   ├── products.py              ← GET /products/{id}, /history
│   │   ├── watchlist.py             ← CRUD watchlist
│   │   └── admin.py                 ← stats, tabla, scrape-all
│   └── scheduler/jobs.py            ← scraping automático watchlist
└── frontend/src/
    ├── api/client.ts                ← axios + todos los tipos TS + endpoints
    ├── components/
    │   ├── Navbar.tsx               ← sync con URL query param
    │   └── ProductCard.tsx          ← ML (amarillo) / Amazon (naranja) / Frávega (azul)
    └── pages/
        ├── Home.tsx                 ← categorías + búsquedas populares
        ├── SearchResults.tsx        ← 1/2/3 columnas según fuentes con resultados
        ├── ProductDetail.tsx        ← gráfico Recharts + stats + watchlist
        ├── Watchlist.tsx            ← tabla semáforo verde/rojo
        └── Admin.tsx                ← stats + tabla paginada
```

---

## API ENDPOINTS

```
GET  /health
GET  /categories

GET  /search?q=...&cat=slug&limit=10
     → { query, ml: [...], fravega: [...], amazon: [...] }

GET  /products/{id}
GET  /products/{id}/history
POST /products/{id}/scrape

GET    /watchlist
POST   /watchlist  { product_id, alerta_pct }
DELETE /watchlist/{id}

GET  /admin/products?source=&cat=
GET  /admin/stats
POST /admin/scrape-all
```

---

## ESTADO ACTUAL DE SCRAPERS

| Scraper | Local | Producción (Render) | Motivo |
|---|---|---|---|
| MercadoLibre | ✅ funciona | ✅ funciona | httpx puro, sin anti-bot |
| Amazon | ✅ Playwright | ✅ **funciona** (curl_cffi) | curl_cffi imita TLS fingerprint de Chrome |
| Frávega | ✅ funciona | ❌ geo-blocked | Cloudflare de Frávega bloquea IPs no-AR |

**Amazon en producción:** resuelto con `curl_cffi==0.7.4` (`impersonate="chrome124"`).

**Frávega en producción:** Cloudflare JS challenge. Diagnóstico confirmado:
- Render recibe 919 bytes → es la página de challenge de Cloudflare (no contenido real)
- curl_cffi bypassea TLS fingerprint pero no ejecuta el JS del challenge
- IP de datacenter (Render Oregon) es flaggeada automáticamente por Cloudflare
- Funciona perfecto local (IP argentina = IP "humana" confiable para Cloudflare)

**Tres opciones pendientes de decisión (próxima sesión):**
- **A** Railway São Paulo (IP sudamericana, gratis) — migrar backend o solo scraper
- **B** GitHub Actions cron (scrapea y cachea en DB cada 6h, gratis)
- **C** Aceptar ML+Amazon en prod, Frávega en local — seguir con P1 UX

**Técnica de parseo Frávega:** lee `__NEXT_DATA__` Apollo GraphQL cache en JSON — más robusto que HTML scraping.
- Price: `salePrice.amounts[0].min`
- Image URL: `https://images.fravega.com/f300/{filename}`
- URL: `https://www.fravega.com/producto/{slug}/`

---

## MEJORAS PENDIENTES (priorizadas)

### P0 — Crítico para portfolio
- [x] **Amazon en producción** — resuelto con curl_cffi (impersonate Chrome TLS)
- [ ] **Frávega en producción** — geo-blocked por Cloudflare. Requiere proxy AR (~$3/mes). Baja prioridad.

### P1 — UX importante
- [ ] **Ordenar resultados por precio** — botón sort asc/desc en SearchResults
- [ ] **Filtro por fuente** — checkbox ML / Frávega / Amazon en SearchResults
- [ ] **Toast notifications** — feedback al agregar/quitar watchlist, al scrapear
- [ ] **Watchlist: alerta configurable** — editar el % de alerta por producto
- [ ] **Meta tags SEO** — og:title, og:description, og:image en index.html

### P2 — Calidad y completitud
- [ ] **README con screenshots** — capturas reales del sitio para el portfolio
- [ ] **Rotar Render API key** — la key anterior fue expuesta (ver .env local)
- [ ] **DB expira 2026-05-25** — crear nueva instancia PostgreSQL en Render antes de esa fecha
- [ ] **APScheduler: scraping de products** — actualmente solo scrapea watchlist, no búsquedas frecuentes
- [ ] **Gráfico con más datos** — el historial necesita tiempo para acumular puntos; agregar datos demo

### P3 — Mejoras futuras
- [ ] Light/dark mode toggle
- [ ] Comparación directa de precios entre fuentes (mismo producto en ML vs Amazon)
- [ ] Exportar watchlist a CSV
- [ ] Dominio custom
- [ ] PWA / notificaciones push para alertas de precio

---

## DISEÑO UI — PALETA

- Fondo: `#0f172a` (dark navy)
- Cards: `#1e293b` (slate-800)
- Accent: `#3b82f6` (blue-500)
- Fuentes badge: ML `bg-yellow-500` / Amazon `bg-orange-500` / Frávega `bg-blue-500`
- Semáforo watchlist: verde bajó / rojo subió / gris sin cambio

---

## SCRAPING — GOTCHAS CLAVE

### MercadoLibre
- Selector precio: `span.andes-money-amount__fraction` (poly-card)
- Funciona en prod porque Render tiene IP de EEUU pero ML AR no bloquea httpx
- Headers: `Accept-Language: es-AR`

### Amazon
- Selector precio: `span.a-price-whole` + `span.a-price-fraction`
- `USE_PLAYWRIGHT=true` (default) → Playwright local; `false` → httpx prod
- httpx con timeout 8s, 1 intento (falla rápido en prod para no bloquear la búsqueda)
- Anti-bot detecta httpx en prod: solución definitiva = ScraperAPI

### Frávega
- URL: `https://www.fravega.com/l/?keyword={query}`
- Selector: `article` → `a[href]`, `img[src]`, `span` con precio `$999.999`
- Playwright local funciona. httpx fallback pendiente (P0).

---

## REGLAS DE EJECUCIÓN

1. **Leer STATUS.md primero** — estado exacto de la sesión anterior
2. **Actualizar STATUS.md + CLAUDE.md** después de cambios importantes
3. **Si algo falla** → diagnosticar puntualmente, no reescribir todo
4. **Screenshots con Playwright** para verificar UI después de cambios visuales
5. **Nunca hardcodear secretos** — usar `.env` local + variables de entorno en Render/Vercel
6. **Tokens:** código completo, explicaciones mínimas

---

## CREDENCIALES (NUNCA en git)
```
Render owner ID: tea-d657ionpm1nc739k5mig
Render Service:  srv-d7mjgju8bjmc738cpsd0
GitHub user:     thestrokes1
Gmail:           fathercyborg@gmail.com
```
Ver `.env` local para DATABASE_URL, RENDER_API_KEY, EMAIL_PASSWORD.

---

## TROUBLESHOOTING

| Error | Causa | Fix |
|---|---|---|
| Amazon 0 resultados en prod | Anti-bot bloquea httpx | ScraperAPI (pendiente P0) |
| Frávega 0 resultados en prod | Playwright no en Render | httpx fallback (pendiente P0) |
| `ModuleNotFoundError` | venv no activado | activar venv |
| `CORS error` | origin no permitido | verificar `allow_origins` en FastAPI |
| `DB locked` | SQLAlchemy session no cerrada | usar `async with` |
| `Vite not found` | node_modules no instalado | `npm install` en /frontend |
| Render duerme | Free tier duerme tras 15min inactividad | primer request lento (~30s cold start) |
