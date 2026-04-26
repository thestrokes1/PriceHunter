# STATUS.md — PriceHunter
> Actualizar después de CADA paso completado.

---

## ESTADO GENERAL
**Fase actual:** Post-deploy — mejoras iterativas  
**Último paso:** Amazon resuelto con curl_cffi. Frávega diagnosticado (Cloudflare JS challenge). Ver FRAVEGA PENDIENTE abajo.  
**Próximo paso (próxima sesión):** Elegir opción para Frávega prod (A/B/C) → luego P1 UX (sort, filtros, toasts)

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
- [ ] README con screenshots (P2)
- [ ] Rotar Render API key comprometida (P2)

---

## FRÁVEGA EN PRODUCCIÓN — DECISIÓN PENDIENTE

**Diagnóstico confirmado (2026-04-26):**
- Render recibe 919 bytes de Fravega → es una **Cloudflare JS challenge** (no geo-block)
- curl_cffi bypassea TLS fingerprint pero NO puede ejecutar el JavaScript del challenge
- IP de datacenter conocida (Render Oregon) → Cloudflare desconfía automáticamente

**Tres opciones disponibles, elegir al inicio de próxima sesión:**

**A — Railway São Paulo** (gratis)
- Railway tiene servidores en Brasil (IP sudamericana, no datacenter flaggeado)
- Migrar solo el scraper de Frávega a un servicio Railway, o todo el backend
- Costo: $0 (entra en el free credit de $5/mes de Railway)
- Trabajo: ~1-2h de configuración

**B — GitHub Actions cron** (gratis)
- Cron job cada 6h que scrapea Frávega desde IP de GitHub (puede o no pasar Cloudflare)
- Guarda resultados en la DB → `/search` sirve datos cacheados para Frávega
- Costo: $0
- Datos: no son "live", se actualizan cada X horas
- Trabajo: ~1h de configuración

**C — Aceptar ML + Amazon en producción** (gratis, sin trabajo)
- Frávega funciona perfecto en local (IP argentina)
- Para el portfolio se demuestra en vivo desde la máquina de Cristian
- Seguir con mejoras P1 directamente

---

### MEJORAS POST-DEPLOY ✅ (sesión 2026-04-26)
- [x] Frávega como tercer scraper (Playwright local)
- [x] Frávega httpx fallback para producción
- [x] Amazon timeout 8s, sin retry (era 2×20s = 40s+)
- [x] Navbar sync con URL query param
- [x] Columnas vacías ocultas en SearchResults
- [x] Grid adaptativo (1/2/3 cols según resultados)
- [x] Page title: "PriceHunter — Comparador de precios"
- [x] Admin: paginación (20/página) + filtro por fuente + badge Frávega
- [x] CLAUDE.md reescrito con estado real y backlog priorizado

### Sesión 2026-04-26 (tarde)
- [x] Amazon en producción resuelto: curl_cffi impersonate=chrome124 → 5 resultados USD reales
- [x] Frávega scraper mejorado: lee Apollo GraphQL JSON (__NEXT_DATA__) en vez de HTML
- [x] Frávega FRAVEGA_PROXY env var implementada (plug-and-play cuando se tenga proxy)
- [x] Diagnóstico Frávega prod: 919 bytes = Cloudflare JS challenge (no geo-block)
- [x] Tres opciones documentadas (A/B/C) para resolver Frávega en prod sin costo
- [ ] **PENDIENTE: elegir opción A/B/C para Frávega prod**

### Sesión 2026-04-26 (noche) — P1 UX
- [x] Fix grid layout: lg:grid-cols-2 → md:grid-cols-2 (viewport ~929px no activaba lg=1024px)
- [x] Sort por precio: botón cicla none→asc→desc, aplica a todas las columnas simultáneamente
- [x] Filtros por fuente: toggles ML/Frávega/Amazon — solo muestra fuentes con resultados
- [x] Toast notifications: verde "Agregado ✓" / rojo "Eliminado" en SearchResults + ProductDetail
- [x] Animación fade-in custom en tailwind.config.js
- [x] Commit ea3fe68 + deploy Vercel → producción
- [x] Watchlist alerta % editable inline (PATCH /watchlist/{id}) — commit 65c54cd
- [x] Meta tags SEO en index.html (og:title, og:description, twitter:card)
- [x] Vercel deploy manual (vercel --prod) — Render auto-deploy desde git push

### P1 COMPLETO — Todas las mejoras UX implementadas y en producción

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
