# STATUS.md — PriceHunter
> Actualizar después de CADA paso completado.

---

## ESTADO GENERAL
**Fase actual:** 0 — Setup inicial  
**Último paso:** CLAUDE.md y STATUS.md creados  
**Próximo paso:** Crear repo en GitHub → venv → dependencias backend

---

## CHECKLIST

### FASE 1 — Setup y DB
- [x] CLAUDE.md creado
- [x] STATUS.md creado
- [ ] Repo GitHub `pricehunter` creado
- [ ] venv Python creado (D:\Pricehunter\venv)
- [ ] backend/requirements.txt + dependencias instaladas
- [ ] Node.js instalado y verificado
- [ ] frontend/ creado con React + Vite + TS + Tailwind
- [ ] PostgreSQL creado en Render via API
- [ ] DATABASE_URL seteada en .env
- [ ] SQLAlchemy models creados (categories, products, price_history, watchlist)
- [ ] init_db.py corre sin errores + seed categorías insertado
- [ ] FastAPI /health responde OK
- [ ] FastAPI /categories devuelve las 8 categorías

### FASE 2 — Scrapers
- [ ] ml_scraper.py: busca por keyword, devuelve lista productos
- [ ] amazon_scraper.py: busca en amazon.com, devuelve lista productos
- [ ] GET /search?q=notebook funciona (ML + Amazon en paralelo)
- [ ] Resultados se guardan en DB

### FASE 3 — API completa
- [ ] GET /products/{id} + /history
- [ ] POST/GET/DELETE /watchlist
- [ ] POST /admin/products (agregar por URL)
- [ ] POST /admin/scrape-all
- [ ] APScheduler corriendo

### FASE 4 — Frontend
- [ ] Navbar + routing
- [ ] Home: categorías + buscador
- [ ] SearchResults: ML vs Amazon
- [ ] ProductDetail: gráfico + stats
- [ ] Watchlist
- [ ] Admin panel

### FASE 5 — Deploy
- [ ] Backend → Render
- [ ] Frontend → Vercel
- [ ] README con screenshots

---

## NOTAS TÉCNICAS
_Se irán agregando durante el desarrollo._

---

## LOG DE SESIONES

### Sesión 1 (2026-04-25)
- Proyecto planificado desde TrackPrice session
- CLAUDE.md y STATUS.md creados
- Stack decidido: FastAPI + SQLAlchemy + React + Vite + TS + Tailwind + Recharts
- Directorio: D:\Pricehunter
