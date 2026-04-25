# PRICEHUNTER — CLAUDE.md
> Leer esto PRIMERO en cada sesión. Contiene todo el contexto necesario.

---

## PROYECTO
Comparador y tracker de precios multi-plataforma.
Busca productos en **MercadoLibre Argentina** y **Amazon.com** simultáneamente,
guarda historial de precios, permite armar una watchlist personal y tiene panel de control.
**Objetivo:** Portfolio laboral de Cristian — proyecto flagship completo y profesional.

## DUEÑO
Cristian — Python, JS/TS, Android (Kotlin), iOS, Java.
No hace nada manualmente — Claude ejecuta todo en terminal.
Claude tiene acceso global a Chrome (`start chrome "url"`) y puede controlarlo con Playwright.
Claude tiene acceso a Render via API key.

## DIRECTORIO RAÍZ
```
D:\Pricehunter
```

## CREDENCIALES Y ACCESOS (nunca commitear)
```
Render API key:  rnd_hJdKQnuz1Y7daw5iCcBUFwt4A9At
Render owner ID: tea-d657ionpm1nc739k5mig
GitHub user:     thestrokes1
Email Gmail:     fathercyborg@gmail.com
```

---

## STACK DECIDIDO (no cambiar sin actualizar este archivo)

| Capa | Herramienta | Motivo |
|---|---|---|
| Backend | FastAPI + Python 3.11 | rendimiento, tipado, OpenAPI gratis |
| ORM | SQLAlchemy 2.0 (async) | profesional, relaciones complejas |
| Validación | Pydantic v2 | integrado con FastAPI |
| Base de datos | PostgreSQL (Render) | producción, historial |
| Scraping | httpx + async + BeautifulSoup4 | scraping paralelo ML + Amazon |
| Scheduler | APScheduler | scraping automático en background |
| Frontend | React 18 + Vite + TypeScript | componentes, admin panel |
| Estilos | Tailwind CSS v3 | rápido, profesional |
| Gráficos | Recharts | nativo React, limpio |
| Routing | React Router v6 | |
| HTTP client | TanStack Query + axios | cache, loading states |
| Iconos | Lucide React | |
| Deploy API | Render (free tier) | |
| Deploy Frontend | Vercel (free) | |
| Entorno Python | venv en D:\Pricehunter\venv | |
| Entorno Node | D:\Pricehunter\frontend\ | |

---

## ESTRUCTURA DE CARPETAS
```
D:\Pricehunter
├── CLAUDE.md                        ← este archivo
├── STATUS.md                        ← estado actual (actualizar siempre)
├── .env                             ← secretos (nunca en git)
├── .env.example
├── .gitignore
├── render.yaml
├── README.md
│
├── backend/
│   ├── main.py                      ← FastAPI app + routers
│   ├── config.py                    ← settings desde .env
│   ├── requirements.txt
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py              ← engine SQLAlchemy, get_db
│   │   ├── models.py                ← tablas ORM
│   │   └── init_db.py               ← crear tablas + seed categorías
│   │
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── ml_scraper.py            ← búsqueda + precio en MercadoLibre AR
│   │   ├── amazon_scraper.py        ← búsqueda + precio en Amazon.com
│   │   └── utils.py                 ← headers, delays, helpers
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── search.py                ← GET /search
│   │   ├── products.py              ← GET /products/{id}, historial
│   │   ├── watchlist.py             ← CRUD watchlist
│   │   └── admin.py                 ← panel de control
│   │
│   └── scheduler/
│       └── jobs.py                  ← scraping automático cada X horas
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        │   └── client.ts            ← axios instance + endpoints
        ├── components/
        │   ├── Navbar.tsx
        │   ├── SearchBar.tsx
        │   ├── ProductCard.tsx      ← card ML o Amazon
        │   ├── PriceChart.tsx       ← Recharts
        │   ├── WatchlistButton.tsx
        │   └── CategoryGrid.tsx
        └── pages/
            ├── Home.tsx             ← categorías + buscador
            ├── SearchResults.tsx    ← ML vs Amazon lado a lado
            ├── ProductDetail.tsx    ← historial + gráfico
            ├── Watchlist.tsx        ← mi lista
            └── Admin.tsx            ← panel de control
```

---

## BASE DE DATOS — SCHEMA

```sql
-- Categorías predefinidas
CREATE TABLE categories (
    id      SERIAL PRIMARY KEY,
    nombre  TEXT NOT NULL,
    slug    TEXT UNIQUE NOT NULL,
    icono   TEXT,                    -- emoji o nombre de icono Lucide
    color   TEXT                     -- hex color para UI
);

-- Productos scrapeados (resultado de búsquedas)
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    url         TEXT NOT NULL UNIQUE,
    source      TEXT NOT NULL,       -- 'mercadolibre' | 'amazon'
    category_id INTEGER REFERENCES categories(id),
    imagen_url  TEXT,
    rating      REAL,
    reviews     INTEGER,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Historial de precios
CREATE TABLE price_history (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price       REAL NOT NULL,
    currency    TEXT DEFAULT 'USD',  -- 'ARS' para ML, 'USD' para Amazon
    scraped_at  TIMESTAMP DEFAULT NOW()
);

-- Watchlist del usuario
CREATE TABLE watchlist (
    id                  SERIAL PRIMARY KEY,
    product_id          INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    alerta_pct          REAL DEFAULT 5.0,    -- alertar si baja X%
    precio_al_agregar   REAL,
    added_at            TIMESTAMP DEFAULT NOW(),
    UNIQUE(product_id)
);
```

**Seed categorías:**
```python
[
    {"nombre": "Tecnología",    "slug": "tecnologia",   "icono": "💻", "color": "#3b82f6"},
    {"nombre": "Celulares",     "slug": "celulares",    "icono": "📱", "color": "#8b5cf6"},
    {"nombre": "Motos",         "slug": "motos",        "icono": "🏍️", "color": "#f59e0b"},
    {"nombre": "Autos",         "slug": "autos",        "icono": "🚗", "color": "#ef4444"},
    {"nombre": "Instrumentos",  "slug": "instrumentos", "icono": "🎸", "color": "#10b981"},
    {"nombre": "Hogar",         "slug": "hogar",        "icono": "🏠", "color": "#6b7280"},
    {"nombre": "Deportes",      "slug": "deportes",     "icono": "⚽", "color": "#f97316"},
    {"nombre": "Ropa",          "slug": "ropa",         "icono": "👕", "color": "#ec4899"},
]
```

---

## API ENDPOINTS

Base URL prod: `https://pricehunter-api.onrender.com` (crear en Render)

```
GET  /health                         → estado + DB
GET  /categories                     → lista categorías

GET  /search?q=query&cat=slug&limit=10
     → busca en ML y Amazon en paralelo
     → { ml: [...], amazon: [...] }

GET  /products/{id}                  → detalle producto
GET  /products/{id}/history          → historial precios
POST /products/{id}/scrape           → forzar scraping ahora

GET  /watchlist                      → mi lista
POST /watchlist { product_id, alerta_pct }
DELETE /watchlist/{id}

GET  /admin/products?source=&cat=    → todos los productos trackeados
POST /admin/products { url, category_id }   → agregar por URL
GET  /admin/stats                    → métricas generales
POST /admin/scrape-all               → forzar scraping de toda la watchlist
```

---

## FRONTEND — PÁGINAS

### Home (`/`)
- Navbar con logo + buscador + link watchlist
- Grid de categorías (8 cards con color e icono)
- Sección "Trending" con productos más trackeados

### Search Results (`/search?q=...&cat=...`)
- Dos columnas: MercadoLibre | Amazon
- Cada card: imagen, título (truncado), precio, fuente, botón watchlist
- Filtros: categoría, ordenar por precio
- Loading skeleton mientras scrapeá

### Product Detail (`/product/:id`)
- Header: nombre, imagen, precio actual, fuente
- Badge: ↑ +12% vs hace 30 días / ↓ -5% mínimo histórico
- Gráfico Recharts: historial de precios
- Stats: precio mínimo, máximo, promedio
- Botón "Ver en [ML/Amazon]"
- Botón "Agregar a watchlist"

### Watchlist (`/watchlist`)
- Tabla de productos guardados
- Columnas: producto, precio al guardar, precio actual, variación %, alerta
- Color: verde si bajó, rojo si subió
- Botón eliminar

### Admin (`/admin`)
- Form para agregar producto por URL
- Tabla de todos los productos en DB
- Botón "Scrapear ahora" por producto
- Botón "Scrapear todos"
- Stats: total productos, última corrida, errores

---

## FASES DE EJECUCIÓN

### FASE 1 — Setup y DB
- [ ] Crear repo en GitHub (`pricehunter`)
- [ ] venv Python + dependencias backend
- [ ] Node + dependencias frontend (React + Vite + TS + Tailwind)
- [ ] PostgreSQL en Render (via API)
- [ ] SQLAlchemy models + init_db con seed categorías
- [ ] FastAPI con /health y /categories funcionando

### FASE 2 — Scrapers
- [ ] ml_scraper.py: buscar por keyword → lista de productos con precio
- [ ] amazon_scraper.py: buscar en amazon.com → lista de productos con precio
- [ ] Endpoint /search funcionando con ambos en paralelo
- [ ] Guardar resultados en DB (products + price_history)

### FASE 3 — API completa
- [ ] GET /products/{id} + /history
- [ ] CRUD watchlist
- [ ] POST /admin/products (agregar por URL)
- [ ] POST /admin/scrape-all
- [ ] APScheduler: scraping automático cada 6h

### FASE 4 — Frontend
- [ ] Setup React + Vite + TS + Tailwind
- [ ] Navbar + routing
- [ ] Home: categorías + buscador
- [ ] SearchResults: ML vs Amazon
- [ ] ProductDetail: gráfico + stats
- [ ] Watchlist: tabla con variaciones
- [ ] Admin: panel de control

### FASE 5 — Deploy
- [ ] Backend → Render (nuevo servicio)
- [ ] Frontend → Vercel
- [ ] Variables de entorno en producción
- [ ] README con screenshots
- [ ] Dominio custom (opcional)

---

## REGLAS DE EJECUCIÓN

1. **Leer STATUS.md primero** — saber exactamente dónde estamos
2. **Actualizar STATUS.md** después de cada paso exitoso
3. **Si algo falla** → diagnosticar puntualmente, no reescribir todo
4. **Orden:** instalar → crear → probar → confirmar → siguiente
5. **Nunca asumir instalado** → verificar con `pip list` o `node -v`
6. **Un archivo a la vez** — probar antes de pasar al siguiente
7. **Mostrar en Chrome** después de cada cambio visual significativo
8. **Screenshots** con Playwright headless para verificar UI sin interacción manual
9. **Usar Render API** (`rnd_hJdKQnuz1Y7daw5iCcBUFwt4A9At`) para crear/gestionar servicios
10. **Tokens:** respuestas cortas. Código completo, explicaciones mínimas.

---

## VARIABLES DE ENTORNO (.env)
```
# Base de datos
DATABASE_URL=postgresql://...

# Email alertas
EMAIL_SENDER=fathercyborg@gmail.com
EMAIL_PASSWORD=zklsbovgytlbkzzv
EMAIL_RECEIVER=fathercyborg@gmail.com

# API
SECRET_KEY=pricehunter-secret-2026
SCRAPE_API_KEY=pricehunter-scrape-2026

# Frontend (Vite)
VITE_API_URL=https://pricehunter-api.onrender.com
```

---

## SCRAPING — NOTAS IMPORTANTES

### MercadoLibre Argentina
- URL de búsqueda: `https://www.mercadolibre.com.ar/jm/search?as_word={query}&category={cat_id}`
- Selector precio: `span.andes-money-amount__fraction`
- Selector título: `h2.ui-search-item__title`
- Selector imagen: `img.ui-search-result-image__element`
- **Funciona desde IPs argentinas. Desde EEUU devuelve 403.**
- Usar headers con Accept-Language: es-AR

### Amazon.com
- URL de búsqueda: `https://www.amazon.com/s?k={query}`
- Selector precio: `span.a-price-whole`
- Selector título: `span.a-size-medium.a-color-base.a-text-normal` o `h2 a span`
- Selector imagen: `img.s-image`
- **Amazon tiene anti-bot. Usar delays 2-5s + headers realistas + User-Agent rotativo**
- Si bloquea: probar con `amazon.com/s?k={query}&ref=nb_sb_noss`
- Moneda: USD → mostrar en frontend como USD con conversión informativa a ARS

---

## DISEÑO UI — GUÍA

- **Paleta:** fondo `#0f172a` (dark navy), cards `#1e293b`, accent `#3b82f6` (azul)
- **Alternativa light mode:** fondo `#f8fafc`, cards `white`
- **Tipografía:** Inter o system-ui
- **Cards productos:** imagen izquierda, info derecha, badge de fuente (ML amarillo / Amazon naranja)
- **Gráfico:** línea azul, fondo semi-transparente, tooltips con precio formateado
- **Watchlist:** tabla con colores semáforo (verde bajó / rojo subió / gris sin cambio)

---

## ANTI-PATTERNS
- ❌ No usar Selenium
- ❌ No hardcodear credenciales
- ❌ No scrapear sin delays (mínimo 1-3s ML, 2-5s Amazon)
- ❌ No crear múltiples archivos sin testear el anterior
- ❌ No ignorar errores HTTP
- ❌ No bloquear el event loop en FastAPI (usar async/await)
- ❌ No hacer fetch en componentes sin TanStack Query

---

## TROUBLESHOOTING

| Error | Causa | Fix |
|---|---|---|
| `403 Amazon` | Anti-bot detectó scraper | rotar User-Agent, aumentar delay |
| `ModuleNotFoundError` | venv no activado | activar venv |
| `CORS error` | frontend no puede llamar API | verificar `allow_origins` en FastAPI |
| `Hydration error` | React SSR mismatch | revisar renders condicionales |
| `DB locked` | SQLAlchemy session no cerrada | usar `async with` correctamente |
| `Vite not found` | node_modules no instalado | `npm install` en /frontend |
