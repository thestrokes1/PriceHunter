# STATUS.md — PriceHunter
> Actualizar después de CADA paso completado.

---

## ESTADO GENERAL
**Fase actual:** 2 — Scrapers  
**Último paso:** Frontend completo + Backend funcionando con DB  
**Próximo paso:** Probar scrapers ML + Amazon, luego deploy en Render + Vercel

---

## CHECKLIST

### FASE 1 — Setup y DB ✅ COMPLETA
- [x] CLAUDE.md creado
- [x] STATUS.md creado
- [x] Repo GitHub `PriceHunter` creado + push inicial
- [x] venv Python creado (D:\Pricehunter\venv)
- [x] backend/requirements.txt + dependencias instaladas
- [x] Node.js v22 instalado y verificado
- [x] frontend/ creado con React + Vite + TS + Tailwind + TanStack Query + Recharts
- [x] PostgreSQL en Render (reutilizando trackprice-db)
- [x] DATABASE_URL seteada en .env
- [x] SQLAlchemy models creados (categories, products, price_history, watchlist)
- [x] init_db.py corre sin errores + 8 categorías insertadas
- [x] FastAPI /health responde OK + DB conectada
- [x] FastAPI /categories devuelve las 8 categorías
- [x] .claude/settings.json con allowlist de permisos

### FASE 2 — Scrapers (EN CURSO)
- [x] ml_scraper.py: estructura lista
- [x] amazon_scraper.py: estructura lista
- [ ] Probar /search?q=notebook → resultados reales
- [ ] Verificar guardado en DB (products + price_history)

### FASE 3 — API completa
- [x] GET /products/{id} + /history (implementado, sin testear con datos)
- [x] POST/GET/DELETE /watchlist (implementado)
- [x] POST /admin/products (implementado)
- [x] POST /admin/scrape-all (implementado)
- [x] APScheduler configurado (cada 6h)

### FASE 4 — Frontend ✅ COMPLETA
- [x] Navbar + routing (React Router v6)
- [x] Home: categorías + buscador + búsquedas populares
- [x] SearchResults: ML vs Amazon lado a lado + skeletons
- [x] ProductDetail: gráfico Recharts + stats min/max/avg
- [x] Watchlist: tabla semáforo verde/rojo
- [x] Admin: stats + tabla productos + scrape-all

### FASE 5 — Deploy
- [ ] Backend → Render (crear servicio web)
- [ ] Frontend → Vercel
- [ ] Variables de entorno en producción
- [ ] README con screenshots

---

## NOTAS TÉCNICAS

- DB Render: `dpg-d7mdrc9f9bms73fv2h7g-a` (trackprice-db, reutilizada)
- Backend corre en: http://localhost:8000
- Frontend corre en: http://localhost:5173
- PYTHONPATH=. necesario para importar backend como módulo
- Emojis del seed se guardan correctamente en PostgreSQL UTF-8

---

## LOG DE SESIONES

### Sesión 1 (2026-04-25)
- Proyecto planificado desde TrackPrice session
- CLAUDE.md y STATUS.md creados

### Sesión 2 (2026-04-25)
- Fase 1 completa: venv, requirements, DB Render, models, init_db, /health, /categories
- Fase 4 completa: React + Vite + TS + Tailwind + todas las páginas
- .claude/settings.json con allowlist para reducir prompts de permisos
- Build frontend exitoso, UI verificada con Playwright
