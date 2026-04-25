# STATUS.md — PriceHunter
> Actualizar después de CADA paso completado.

---

## ESTADO GENERAL
**Fase actual:** 5 — DEPLOY COMPLETO  
**Último paso:** Backend Render LIVE + Frontend Vercel LIVE  
**Próximo paso:** README con screenshots, mejoras opcionales

---

## URLS DE PRODUCCION
- **Frontend:** https://pricehunter-pied.vercel.app
- **Backend API:** https://pricehunter-api.onrender.com
- **Health check:** https://pricehunter-api.onrender.com/health

---

## CHECKLIST

### FASE 1 — Setup y DB ✅
- [x] Repo GitHub creado (thestrokes1/PriceHunter)
- [x] venv Python + dependencias backend instaladas
- [x] PostgreSQL en Render (trackprice-db, reutilizada)
- [x] SQLAlchemy models + init_db + 8 categorías
- [x] FastAPI /health + /categories funcionando

### FASE 2 — Scrapers ✅
- [x] ml_scraper.py: poly-card selectors, brotli, 10 resultados reales
- [x] amazon_scraper.py: Playwright local / httpx produccion
- [x] GET /search funciona (ML + Amazon secuencial)
- [x] Resultados guardados en DB (upsert)

### FASE 3 — API completa ✅
- [x] GET /products/{id} + /history
- [x] POST/GET/DELETE /watchlist
- [x] POST /admin/products
- [x] POST /admin/scrape-all
- [x] APScheduler (cada 6h)

### FASE 4 — Frontend ✅
- [x] React 18 + Vite + TS + Tailwind v3
- [x] Navbar + routing (React Router v6)
- [x] Home: categorías + buscador + populares
- [x] SearchResults: ML vs Amazon lado a lado + skeletons
- [x] ProductDetail: Recharts + stats min/max/avg + watchlist
- [x] Watchlist: tabla semáforo verde/rojo
- [x] Admin: stats + tabla + scrape-all

### FASE 5 — Deploy ✅
- [x] Backend → Render (pricehunter-api, Python 3.11.7, Oregon)
- [x] Frontend → Vercel (pricehunter-pied.vercel.app)
- [x] DB allowlist abierto a 0.0.0.0/0 para Render
- [x] .gitattributes forzando LF (fix CRLF de Windows)
- [ ] README con screenshots
- [ ] Rotar Render API key comprometida

---

## NOTAS TECNICAS

- DB Render: `dpg-d7mdrc9f9bms73fv2h7g-a` (expira 2026-05-25)
- Render Service: `srv-d7mjgju8bjmc738cpsd0`
- Amazon scraping: Playwright (local) / httpx fallback (produccion)
- ML scraping: httpx + html.parser, brotli decompression
- Windows CRLF issue: .gitattributes resuelve el problema con runtime.txt

---

## LOG DE SESIONES

### Sesion 1 (2026-04-25)
- Proyecto planificado, CLAUDE.md y STATUS.md creados

### Sesion 2 (2026-04-25)
- FASE 1: venv, DB, models, FastAPI /health, /categories
- FASE 4: React + Vite + TS + Tailwind, todas las paginas
- FASE 2: Scrapers ML (poly-card) + Amazon (Playwright)
- FASE 5: Render backend LIVE + Vercel frontend LIVE
- Fix critico: Render API key expuesto (eliminar del historial, rotar)
- Fix: CRLF->LF en runtime.txt via .gitattributes
- Fix: DB IP allowlist 0.0.0.0/0 para acceso desde Render
