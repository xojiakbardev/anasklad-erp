# Anasklad-ERP

> **O'zbek seller'lar uchun MoySklad uslubidagi zamonaviy ERP.**
> Uzum Market bilan to'liq integratsiya, kelajakda Wildberries / Yandex Market uchun ochiq.

Anasklad-ERP — bu O'zbekistondagi marketplace seller'larga kundalik ish uchun yaratilgan butun ERP tizimi: mahsulot katalogi, FBO/FBS omborlar, buyurtmalar, komissiya va sof foyda, ta'minot va qaytarishlar — hammasi bitta panelda.

## Hujjatlar

| Hujjat | Maqsadi |
|--------|---------|
| [`PLAN.md`](./PLAN.md) | Sprint reja, milestone'lar, deliverable'lar |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Backend arxitektura (modular monolith, Dishka, Alembic, outbox, sync worker) |
| [`DESIGN.md`](./DESIGN.md) | Frontend design system: "Terminal of the Silk Road" |
| [`DEPLOY.md`](./DEPLOY.md) | Production deploy guide (VPS + Docker + Caddy + backups) |

## Stack

**Backend:** Python 3.13 · FastAPI · Granian · PostgreSQL 16 · Redis 7 · SQLAlchemy 2 async · Dishka · Arq · Alembic · OpenTelemetry

**Frontend:** React 19 · Vite 6 · TanStack Router/Query/Table · Zustand · Tailwind v4 · shadcn/ui

**Integrations:** Uzum Market Seller OpenAPI (poll-based)

## Tuzilma

```
anasklad-erp/
├── backend/              FastAPI modular monolith
│   └── src/anasklad/
│       ├── core/         framework glue (db, cache, events, obs, security)
│       ├── modules/      auth, catalog, stocks, orders, finance, integrations, sync, reporting, catalog_cost
│       └── connectors/   uzum/, wb/, yandex/
├── frontend/             React 19 admin UI
├── packages/
│   └── uzum-client/      mustaqil Python paket (HTTP qatlam)
└── docker-compose.yml
```

## Ishga tushirish

### Dev (mahalliy)
```bash
docker compose up -d postgres redis
cd backend && alembic upgrade heads && python -m anasklad.granian_entry
cd frontend && pnpm install && pnpm dev
```

### Production (VPS)
Batafsil: [`DEPLOY.md`](./DEPLOY.md)
```bash
git clone https://github.com/xojiakbardev/anasklad-erp.git /opt/anasklad
cd /opt/anasklad && cp .env.example .env  # set secrets
docker compose -f docker-compose.prod.yml up -d
```

## Status

✅ **MVP tayyor** — Sprint 0-8 tugallandi. Bir seller pilot'ga tayyor.

- ✅ Auth (email+password + JWT)
- ✅ Uzum integration (token, shops)
- ✅ Catalog sync (products, variants)
- ✅ FBS orders kanban + actions
- ✅ Finance (sales, expenses, profit)
- ✅ Reports (ABC, turnover, low-stock)
- ✅ Dashboard (KPIs, P&L chart)
- ✅ Uzbek + Russian i18n
- ✅ Onboarding + help center
- ✅ Production Docker + Caddy TLS + CI/CD

Batafsil reja: [`PLAN.md`](./PLAN.md)

---

© 2026 Hojiakbar Nasriddinov
