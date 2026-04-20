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

## Status

🚧 **Sprint 0 — Foundation** (davom etmoqda)

Batafsil: [`PLAN.md`](./PLAN.md)

---

© 2026 Hojiakbar Nasriddinov
