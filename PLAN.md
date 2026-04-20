# Anasklad-ERP — Mahsulot va Texnik Reja

> Versiya 1.0 · 2026-04-20 · Muallif: CTO mas'uliyati (Claude Opus 4.7 yordamida)

Bu hujjat **haqiqat manbai**. Har ikki haftada yangilanadi. Agar kodda va bu hujjatda ziddiyat bo'lsa — kod yutadi, lekin hujjat darhol tuzatiladi.

---

## 1. Mahsulotning maqsadi

**Muammo.** O'zbekistondagi Uzum seller'lar hozirda:
- Uzum seller kabinetida ishlaydi (yaxshi lekin cheklangan analitika)
- Excel'da tannarx hisoblaydi
- Real sof foydani bilmaydi (komissiya + logistika + reklama + qaytarish xarajatini qo'lda yig'adi)
- Qoldiqlarni FBO/FBS bo'yicha alohida kuzatadi
- MoySklad qimmat (5 EUR/oy/user × N user) + rus tili + O'zbek xususiyatlari yo'q

**Yechim.** Anasklad-ERP seller'ga bitta joyda:
1. Real vaqtli **sof foyda** (komissiya, logistika, tannarx, aksiya ayirilgan)
2. FBO + FBS + DBS qoldiqlari yagona jadvalda
3. FBS buyurtmalar kanbani (CREATED → COMPLETED gacha)
4. Ta'minot, qaytarish, xarajatlar jurnali
5. ABC-analiz, P&L, aylanma tezligi hisobotlari
6. **Uzbek + Rus tillari** (majburiy)

**MVP muvaffaqiyat mezonlari (6 oy ichida):**
- 20+ faol seller foydalanuvchi (o'rtacha 2+ soat kunlik sessiya)
- Sof foyda hisoblash aniqligi ±1% (Uzum hisobotiga nisbatan)
- Sinxronizatsiya kechikishi < 3 daqiqa (FBS buyurtma uchun)
- 99.5% uptime

---

## 2. Tamoyillar

1. **Performance — default.** orjson, asyncpg, Granian, tabular-mono numeric, virtual scrolling 1k+ satrlarda. Sekinligi default emas.
2. **Modular monolith, microservice tayyorligi bilan.** Solo dev tezligini saqlaymiz, lekin modullar kelajakda ajratiladigan darajada toza.
3. **YAGNI — lekin qayta yozmaslik.** Bugun kerakmas feature'ni yozmaymiz, lekin sxemani shunday loyihalashtiramizki, qo'shganimizda migratsiya og'riqli bo'lmasin.
4. **Localization birinchi.** Har satr uzb + rus. EN keyin, agar umuman kerak bo'lsa.
5. **Uzum yagona manba emas.** Kod marketplace-agnostic (source="uzum" ustuni). WB/Yandex uchun xuddi shu model.
6. **Kuzatilishi oson.** structlog + OTel + Sentry birinchi kundan. Prod'da "nima bo'ldi?" savoli 5 daqiqada javobini topishi kerak.
7. **Idempotentlik — qonun.** Har sync, har POST retryable bo'lishi kerak. Dublikat yo'q.
8. **Xavfsizlik boshida sodda, keyin kuchaytiriladi.** MVP'da email+pass + JWT. Uzum token'lari Fernet bilan DB'da shifrlangan. Keyin MFA, RBAC, SSO.

---

## 3. Arxitektura (qisqacha)

To'liq versiya: [`ARCHITECTURE.md`](./ARCHITECTURE.md).

- **Backend:** Python 3.13, FastAPI + Granian (Rust ASGI), SQLAlchemy 2 async + asyncpg, Dishka DI, Arq workers, Alembic (modul-branch), PostgreSQL 16 (schema-per-module), Redis 7 (cache + queue + advisory locks), structlog + OpenTelemetry + Sentry.
- **Modullar:** `auth`, `catalog`, `stocks`, `orders`, `finance`, `integrations`, `sync`, `reporting`, `catalog_cost`, `core`.
- **Modullar aro chegara:** `FacadeX` klasslari — boshqa modul faqat shu orqali gaplashadi. ORM entity chegaradan o'tmaydi. import-linter bilan avtomatik tekshiriladi.
- **Transaksion chegara:** bitta request/job — bitta `UnitOfWork` — bitta DB session. Modullar aro mutatsiya outbox orqali emit qilinadi.
- **Multi-tenant:** har jadvalga `tenant_id UUID`. PostgreSQL RLS policy'lari har schema'da.
- **Connector:** `packages/uzum-connector/` — HTTP qatlam. Biznes modullar connector'ga bog'liq emas — faqat `sync` va `integrations` modullari chaqiradi.

## 4. Design tizimi (qisqacha)

To'liq versiya: [`DESIGN.md`](./DESIGN.md).

**Aesthetic:** "Terminal of the Silk Road" — Bloomberg terminalning zichligi + Uzbek ikat ornamenti. Dark mode default. Monospace raqamlar, Fraunces display serif, gold accent. Signature element — **ikat stripe** (har aktiv panel chap chekkasida prosedurali ikat pattern). Signature number — **Ledger number** (tabular-mono, hairline separator, parenthesis negatives).

Never: purple gradient, glassmorphism, rounded pills, Inter (faqat Inter Display), light mode (MVP'da).

---

## 5. Sprint rejasi (8 sprint × 1 hafta)

Har sprint **dushanba boshlanadi**, **juma kechqurun yopiladi**. Shanba — buffer + retrospektiv. Yakshanba — dam olish.

Har sprint oxirida **demo-able deliverable** bo'lishi kerak. Yarim tugallangan qabul qilinmaydi.

### Sprint 0 — Foundation (1 hafta, **hozir**)

**Maqsad:** ishlaydigan skelet + rejalar.

| Vazifa | Deliverable |
|--------|-------------|
| Repo + hujjatlar | `README.md`, `PLAN.md`, `ARCHITECTURE.md`, `DESIGN.md` — push |
| Monorepo skelet | `backend/`, `frontend/`, `packages/`, `docker-compose.yml` — bo'sh lekin tuzilgan |
| `.env.example`, `.gitignore`, `pyproject.toml` | root + submodullar |
| `packages/uzum-connector/` skelet | `pyproject`, `client.py` shell, `README.md` |
| CI skelet | `.github/workflows/ci.yml` — ruff, mypy, pytest (placeholder) |

**Sprint 0 — DONE:** repo push qilingan, sprintlar aniq.

### Sprint 1 — Uzum Connector + Backend skelet (1 hafta)

**Maqsad:** Uzum API'ga ulanib 3 ta endpoint'dan javob olamiz. FastAPI ishga tushadi.

| Vazifa | Deliverable |
|--------|-------------|
| `uzum-connector`: `TokenAuth`, `httpx` client, rate-limit token-bucket (Redis), retry (tenacity) | `UzumClient.get_shops()` ishlaydi |
| `uzum-connector`: endpoint'lar — `/v1/shops`, `/v1/product/shop/{id}`, `/v2/fbs/orders` | Pydantic DTO'lar, respx test'lari |
| Backend: FastAPI + Granian + Dishka container + settings | `/health/live` va `/health/ready` ishlaydi |
| Backend: Alembic init + `core` schema (outbox, audit_log, tenant) | `alembic upgrade heads` ishlaydi |
| Backend: `auth` moduli — User model, JWT (access+refresh), argon2, `/api/auth/login` | Postman'dan login qilib bo'ladi |
| Docker Compose: postgres, redis, api, otel-collector | `docker compose up` → hammasi yashil |

**DoD (Definition of Done):**
- `pytest` 100% yashil (uzum-connector unit + integration, auth e2e)
- `ruff check` va `mypy --strict` xatosiz
- `import-linter` qoidalari yozilgan va o'tadi

### Sprint 2 — Integratsiya moduli (do'kon ulash) (1 hafta)

**Maqsad:** foydalanuvchi Uzum do'konini ulaydi.

| Vazifa | Deliverable |
|--------|-------------|
| `integrations` moduli: `Integration`, `Connection`, `Credential` (Fernet-encrypted) | CRUD API |
| `POST /api/integrations/uzum` — token → `/v1/shops` chaqiradi → shoplarni yozadi | Ulangan do'konlar DB'da |
| `sync.jobs.test_connection` — Arq job, har 1 soatda token haqiqiyligini tekshiradi | DLQ bilan |
| Frontend skeleti: Vite + Tailwind v4 + shadcn + TanStack Router | Login sahifa |
| Frontend: Integrations sahifasi — "Uzum qo'shish" wizard + ulangan do'konlar jadvali | UI ikat-stripe bilan |

**DoD:** Real Uzum token bilan test — ulanadi, do'konlar ko'rinadi.

### Sprint 3 — Katalog sync (1 hafta)

**Maqsad:** Uzum'dan mahsulot + SKU + qoldiqlarni sync qilamiz.

| Vazifa | Deliverable |
|--------|-------------|
| `catalog` moduli: `Product`, `Variant`, `Attribute`, `Image` modellari | migration |
| `stocks` moduli: `StockLedger`, `Reservation`, `Warehouse` | migration, lekin hozirda faqat Uzum yozadi |
| `sync.jobs.sync_catalog` — har 60 daqiqada, chunked, idempotent | cursor.table |
| `sync.jobs.sync_stocks_fbo` — har 5 daqiqada | |
| API: `GET /api/products?shop_id=&filter=&page=` — server-side filter+sort | TanStack Table |
| Frontend: Products sahifasi — virtualized table 1k+ satr, master-detail drawer | Ledger numbers |

**DoD:** 100 SKU bilan test — sync 10 soniyadan kam, UI 60fps bilan skrol.

### Sprint 4 — FBS Orders pipeline (1 hafta)

**Maqsad:** seller'ning asosiy kundalik ishi.

| Vazifa | Deliverable |
|--------|-------------|
| `orders` moduli: `FbsOrder`, `FbsOrderItem`, lifecycle state machine | domain events |
| `sync.jobs.sync_fbs_orders` — har 2 daqiqada, priority=high | |
| FBS actions: `confirm`, `cancel` — facade'lar, stocks reservation bilan | outbox event: `FbsOrderAccepted` |
| Etiketka chop etish: `/v1/fbs/order/{id}/labels/print` → PDF stream | frontend'da "Print" tugmasi |
| Frontend: Orders sahifasi — **kanban 5 ustun** (CREATED/PACKING/PENDING_DELIVERY/DELIVERING/DELIVERED) + list view toggle | drag-to-confirm |
| Frontend: Order detail drawer — items, timer (acceptUntil / deliverUntil), actions | urgent-ring animation |

**DoD:** kanban'da 50 ta order test qilingan, accept → reservation → stock ledger entry.

### Sprint 5 — Finance (sof foyda) (1 hafta)

**Maqsad:** seller "real foyda qancha?" savoliga javob oladi.

| Vazifa | Deliverable |
|--------|-------------|
| `finance` moduli: `Sale`, `Commission`, `Payout`, `Expense` | migration |
| `sync.jobs.sync_fbo_sales` — `/v1/finance/orders` har 10 daqiqada | |
| `sync.jobs.sync_commissions_payouts` — `/v1/finance/expenses` har 1 soatda | |
| `catalog_cost` moduli (bazaviy): `CostLot`, `CostMove` — FIFO | qo'lda purchasePrice kiritiladi (Uzum'dan ham keladi) |
| Hisob: `net_profit = sellerPrice − commission − logisticFee − purchasePrice` | reporting view |
| Frontend: Dashboard sahifasi — **96px Ledger KPI**, P&L chart (gold+teal lines), top SKU list | hairline sweep on sync |
| Frontend: Finance sahifasi — Sales jadvali, Expenses jadvali, Payout reconciliation (tez-tez) | |

**DoD:** haqiqiy sof foyda ±1% aniqlikda Uzum hisobotiga mos keladi.

### Sprint 6 — Reporting + Qoldiqlar (1 hafta)

**Maqsad:** seller qarorlar qabul qila oladi.

| Vazifa | Deliverable |
|--------|-------------|
| `reporting` moduli: materialized views — ABC, turnover, low-stock | daily rebuild job |
| API: `GET /api/reports/abc?period=...` | filter/sort |
| Frontend: Stocks sahifasi — FBO vs FBS split view, low-stock alert | real-time badge |
| Frontend: Reports sahifasi — ABC, aylanma, aksiya/sof narx taqqoslash | export (CSV) |
| Notifications: Redis pub-sub → WebSocket → frontend toast | low stock, new order, sync DLQ |

**DoD:** 1000+ SKU bilan ABC hisoboti < 500ms.

### Sprint 7 — Polish + Pilot seller onboarding (1 hafta)

**Maqsad:** ishlatishga tayyor.

| Vazifa | Deliverable |
|--------|-------------|
| Uzbek + Rus tarjima — barcha UI | i18next, JSON fallback |
| Error handling — har xatolik uchun uzb xabar | `core/http/errors.py` |
| Observability — Sentry, Grafana dashboard (key metrics) | alert rules |
| Onboarding — first-time wizard (integratsiya → sync kuzatish → welcome) | | 
| Help center — 10 ta FAQ sahifa | markdown |
| **1 ta real seller** bilan beta test | 5 ta bug yopildi |

**DoD:** pilot seller 1 hafta foydalanadi, 0 ta kritik bug.

### Sprint 8 — Deploy + launch (1 hafta)

| Vazifa | Deliverable |
|--------|-------------|
| Production infra — Kubernetes (Neon/Contabo/Hetzner) yoki Railway/Render | Terraform / kubectl manifests |
| CI/CD — GitHub Actions → registry → kubectl apply | staging + production env |
| Domain + SSL — anasklad.uz (yoki mavjud) | Cloudflare |
| DB backup — pg_dump har kunlik, 7 kun saqlansin | S3-compatible |
| Monitoring — UptimeRobot + Grafana Cloud | SLO: 99.5% |
| Privacy Policy + Terms — O'zbek huquqiga mos | huquqshunos ko'rigi |
| Marketing sahifa — anasklad.uz landing | next.js yoki astro |

**DoD:** public URL, 10+ seller ro'yxatdan o'tib foydalana oladi.

---

## 6. MVP-dan keyin (Sprint 9+)

Bular Sprint 8 yopilgandan keyin **foydalanuvchi talabiga qarab** prioritezatsiya qilinadi.

| Epic | Ma'nosi |
|------|---------|
| **Tannarx FIFO + Prixod** | Ta'minotchi zakaz, prixod hujjati, o'rtacha/FIFO tannarx |
| **Wildberries konnektor** | Ikkinchi marketplace. Arxitektura tayyor |
| **Telegram bot** | Yangi buyurtma, kritik qoldiq ogohlantirishlari |
| **Reklama ROI** | Uzum reklama xarajati vs sotuv — har SKU bo'yicha |
| **Raqobatchi narxi** | Bir xil SKU boshqa seller'larda qancha turadi |
| **Multi-user + RBAC** | Do'kon ichida xodimlar (admin, hisobchi, ombor) |
| **Mobil PWA** | Ombor ishchisi uchun — shtrix-kod o'qish, prixod |
| **Accounting integratsiya** | 1C, My.SoliqOrgan (keyin) |
| **SaaS billing** | Tarif, Stripe/Click/Payme |

---

## 7. Xavflar va zaxira reja

| Xavf | Ta'siri | Yumshatish |
|------|---------|------------|
| Uzum API sinigan javob qaytaradi | Sync to'xtaydi | Contract test nightly, DLQ, retry bilan |
| Uzum rate-limit noma'lum | 429 xatolar | Adaptive rate limiter (boshida 5 rps, harakat qiladi) |
| Seller API tokenini bermaydi (ishonchsizlik) | MVP'ga seller yo'q | Dastlab o'z do'konimiz bilan ishlaymiz + 1-2 tanish seller |
| Solo dev yonib ketadi | 8 sprint cho'ziladi | Har sprint aniq scope, overtime yo'q, shanba buffer |
| MoySklad/1C O'zbekistonga kiradi | Bozor yoqoladi | Niche (Uzum-first) + tezlik + mahalliy narx |
| PostgreSQL/Redis prod'da yiqiladi | Downtime | Managed DB (Neon yoki Hetzner + DR plan), daily backup |
| Uzum token DB'da qalinlashadi | Xavfsizlik incident | Fernet encrypt at rest + rotation, audit log |

---

## 8. Qaror jurnali (ADR qisqacha)

Har muhim texnik qaror shu yerda. Qaror keyin o'zgarsa — yangi satr, eski satr `~~peretinaydi~~`.

| Sana | Qaror | Sabab |
|------|-------|-------|
| 2026-04-20 | Modular monolith (microservice emas) | Solo dev + speed + extractable boundaries |
| 2026-04-20 | Python 3.13 + FastAPI + Granian | Performance + tanish stack |
| 2026-04-20 | PostgreSQL schema-per-module (prefix emas) | Kelajakda kesib chiqish oson |
| 2026-04-20 | Alembic branch-per-module | Migratsiya konfliktlarini kamaytiradi |
| 2026-04-20 | Transactional outbox (Redis Streams tayyor) | Cross-module decoupling kelajak uchun |
| 2026-04-20 | Dark mode only v1 | Design koherentligi, kuch sarflamaslik |
| 2026-04-20 | Uzbek + Rus only v1 | Target bozor |
| 2026-04-20 | Auth boshida sodda (email+pass+JWT) | MVP tezligi, keyin MFA/SSO |
| 2026-04-20 | Multi-tenant birinchi kundan (tenant_id + RLS) | Qayta yozmaslik; SaaS yo'li ochiq |
| 2026-04-20 | `packages/uzum-connector` — alohida paket | Open-source imkoniyat, HTTP qatlami yakkalangan |

---

## 9. Keyingi qadam

**Hozir:** Sprint 0 tugatish (repo push, docs, skelet).
**Ertaga (Sprint 1 boshlanadi):** `uzum-connector` + backend skelet.

Sizning tasdig'ingiz bilan boshlayman.
