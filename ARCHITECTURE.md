# Anasklad-ERP — Production-Grade Backend Architecture

> Senior-level reference for the backend. Paired with `PLAN.md` (what we ship) and `DESIGN.md` (how it looks).

## 1. Executive Summary & Guiding Principles

Anasklad-ERP is a **modular monolith** built in Python 3.13 on FastAPI/Granian, designed to serve Uzbek Uzum Market sellers with MoySklad-style ERP functionality. The architecture is optimized for three forces that tend to pull in opposite directions:

1. **Speed of iteration** (solo/small team, market changes fast) — monolith, single deploy, one Alembic head tree.
2. **Future extractability** — strict module boundaries enforced by import-linter, so any module can become its own service later.
3. **Poll-based integration reality** — Uzum has no webhooks. The *sync worker* is a first-class citizen, not a background afterthought. Half of the business logic lives there.

Core rule: **no module imports another module's internals**. Cross-module calls go through `Facade` classes registered in Dishka. Domain events are published via an in-process event bus (Redis Streams when extraction happens).

---

## 2. Repository Layout

```
anasklad-erp/
├── pyproject.toml
├── alembic.ini
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── scripts/
│   ├── migrate.py
│   ├── seed_dev.py
│   └── run_worker.py
├── backend/
│   ├── Dockerfile
│   └── src/
│       └── anasklad/
│           ├── __init__.py
│           ├── main.py                  # FastAPI app factory
│           ├── granian_entry.py         # Granian launcher
│           ├── config.py                # pydantic-settings, per-module sub-configs
│           ├── di/
│           │   ├── container.py         # make_async_container(providers=[...])
│           │   ├── core_providers.py    # DB, Redis, HTTP, Settings
│           │   └── app_scope.py         # request/session scopes
│           ├── core/                    # framework glue, NOT business
│           │   ├── db/
│           │   │   ├── base.py          # DeclarativeBase, naming conventions
│           │   │   ├── session.py       # async_sessionmaker
│           │   │   ├── uow.py           # Unit of Work
│           │   │   └── types.py         # Money, TenantId custom types
│           │   ├── cache/
│           │   │   ├── redis.py
│           │   │   └── keys.py          # typed key builders
│           │   ├── events/
│           │   │   ├── bus.py           # InProcEventBus + OutboxRelay
│           │   │   ├── outbox.py        # transactional outbox
│           │   │   └── base.py          # DomainEvent base
│           │   ├── http/
│           │   │   ├── errors.py        # ProblemDetails, exception_handlers
│           │   │   ├── middleware.py    # correlation-id, tenant, structlog ctx
│           │   │   └── deps.py          # CurrentUser, CurrentTenant, Paging
│           │   ├── observability/
│           │   │   ├── logging.py       # structlog + orjson renderer
│           │   │   ├── tracing.py       # OTel setup
│           │   │   └── metrics.py
│           │   ├── security/
│           │   │   ├── jwt.py
│           │   │   ├── hashing.py       # argon2
│           │   │   └── rbac.py
│           │   └── money/
│           │       └── currency.py      # UZS handling, integer tiyin
│           ├── modules/
│           │   ├── auth/
│           │   ├── catalog/
│           │   ├── stocks/
│           │   ├── orders/
│           │   ├── finance/
│           │   ├── integrations/
│           │   ├── sync/
│           │   ├── reporting/
│           │   └── catalog_cost/
│           └── connectors/              # external-world clients (pure I/O)
│               ├── wb/                  # placeholder
│               └── yandex/              # placeholder
├── packages/
│   └── uzum-connector/                  # standalone pip-installable package
├── frontend/
│   └── (Vite + React)
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── fixtures/
│   └── conftest.py
└── .import-linter.ini                   # enforces module boundaries
```

### 2.1 Per-module Layout (canonical)

Every module under `modules/<name>/` follows the same shape:

```
modules/orders/
├── __init__.py
├── provider.py         # Dishka Provider for this module
├── config.py           # OrdersSettings (prefixed env)
├── api/
│   ├── router.py       # APIRouter, only wiring
│   ├── v1/
│   │   ├── fbs.py
│   │   ├── fbo.py
│   │   └── schemas.py  # request/response (pydantic)
│   └── deps.py         # endpoint-local deps only
├── application/        # use-cases (orchestration)
│   ├── commands/
│   │   ├── accept_fbs_order.py
│   │   └── ship_fbs_order.py
│   ├── queries/
│   │   └── list_orders.py
│   └── services/       # internal domain service
│       └── fbs_lifecycle.py
├── domain/             # pure entities/value objects, no I/O
│   ├── entities.py
│   ├── enums.py        # FbsStatus, Scheme
│   └── events.py       # FbsOrderShipped, OrderCompleted
├── infrastructure/
│   ├── models.py       # SQLAlchemy ORM
│   ├── repository.py
│   └── mappers.py      # ORM <-> domain
├── facade.py           # OrdersFacade — public API for OTHER modules
└── tests/
    ├── test_fbs_lifecycle.py
    └── test_repository.py
```

Rule enforced by import-linter:
- `modules.orders.*` may import from `core.*`, `modules.orders.*`.
- It may import **only** `modules.X.facade` from any other module `X` — never `modules.X.domain/application/infrastructure/api`.
- `core.*` may not import any `modules.*`.

---

## 3. Module Boundaries and Communication

### 3.1 Two Styles Coexist

**Synchronous facade calls** — used when a use-case *requires* an answer *now* and you need the result in the same DB transaction (or a tightly related one).

**Domain events via transactional outbox** — used for "fire-and-forget" cross-module reactions (e.g. Finance listens to `FbsOrderCompleted` to create a `Sale`).

This is the MoySklad/Odoo split: queries go through facades; reactions go through events.

### 3.2 Facade Shape

```python
# modules/stocks/facade.py
class StocksFacade:
    def __init__(self, uow: UnitOfWork, cache: StockCache) -> None: ...

    async def get_available(
        self, tenant_id: UUID, variant_id: UUID, warehouse: WarehouseRef
    ) -> Decimal: ...

    async def reserve(
        self, *, tenant_id: UUID, variant_id: UUID,
        qty: Decimal, order_ref: str, idempotency_key: str,
    ) -> ReservationId:
        """Reserve stock for an FBS order. Idempotent by order_ref+variant_id."""

    async def write_off(
        self, *, reservation_id: ReservationId, reason: WriteOffReason,
    ) -> StockLedgerEntryId: ...
```

`StocksFacade` is the **only** symbol exported from the `stocks` module for external consumers. Its methods accept primitive types + DTOs. No SQLAlchemy session leakage; no ORM entities across boundary.

### 3.3 Inter-module Call Example

```python
# modules/orders/application/commands/accept_fbs_order.py
class AcceptFbsOrderCommand:
    def __init__(
        self,
        uow: UnitOfWork,
        orders_repo: OrdersRepository,
        stocks: StocksFacade,        # <- injected via Dishka
        catalog: CatalogFacade,
        bus: EventBus,
    ) -> None: ...

    async def __call__(self, payload: AcceptFbsOrderDTO) -> FbsOrderId:
        async with self.uow:
            variant = await self.catalog.get_variant(payload.variant_id)
            reservation = await self.stocks.reserve(
                tenant_id=payload.tenant_id,
                variant_id=variant.id,
                qty=payload.qty,
                order_ref=payload.uzum_order_id,
                idempotency_key=f"fbs:{payload.uzum_order_id}:{variant.id}",
            )
            order = FbsOrder.accept(payload, reservation_id=reservation)
            await self.orders_repo.add(order)
            await self.bus.publish(FbsOrderAccepted(order_id=order.id))
            await self.uow.commit()
        return order.id
```

Both `orders` and `stocks` write in the **same SQLAlchemy session** because `UnitOfWork` is request-scoped.

### 3.4 Event Bus

Events flow through the **transactional outbox pattern**:

1. Use-case appends event to `core.outbox` table in the same transaction that mutates domain tables.
2. `OutboxRelay` (Arq cron every 1s, locked by `pg_try_advisory_lock`) reads unsent rows and dispatches to in-proc handlers; on success marks `sent_at`.
3. When a module is extracted, `OutboxRelay` changes its sink from in-proc bus to Redis Streams / NATS — domain code doesn't change.

---

## 4. Dishka DI Organization

**Per-module providers + one root container.** Each module owns a `provider.py`; `main.py` composes them.

```python
# modules/orders/provider.py
class OrdersProvider(Provider):
    scope = Scope.REQUEST

    orders_repository = provide(OrdersRepository)
    accept_fbs_cmd    = provide(AcceptFbsOrderCommand)
    ship_fbs_cmd      = provide(ShipFbsOrderCommand)

    @provide(scope=Scope.APP)
    def facade(self, session_factory: AsyncSessionFactory) -> OrdersFacade: ...
```

Scopes:
- `APP` — engine, redis pool, settings, Uzum client factory, facades (stateless).
- `REQUEST` — session, UoW, repositories, command/query handlers, CurrentUser.
- **Workers** use the same container with a custom `Scope.REQUEST`-equivalent per-job context manager.

---

## 5. Database Schema Strategy

**PostgreSQL schemas per module, not table prefixes.**

```
DB: anasklad
├── schema auth          (users, sessions, refresh_tokens)
├── schema catalog       (products, variants, attributes)
├── schema stocks        (stock_ledger, reservations, warehouses)
├── schema orders        (fbs_orders, fbs_items, fbo_sales)
├── schema finance       (sales, commissions, payouts, expenses)
├── schema integrations  (integrations, connections, credentials)
├── schema sync          (sync_runs, cursors, dlq)
├── schema reporting     (materialized views, rollups)
├── schema cost          (cost_lots, cost_moves)
└── schema core          (outbox, advisory_locks, audit_log)
```

Reasons:
1. Extracting a module later = `pg_dump -n schema_name` → new DB.
2. **No cross-schema FKs** — cross-module references are plain UUIDs. Enforces the boundary at DB level.
3. Per-schema `search_path` in tests gives isolated testing.
4. Role-based grants can be per-schema (e.g., read-only analytics user gets only `reporting`).

**Money type**: always `NUMERIC(18,2)` for UZS; `Decimal` in Python.

**Multi-tenancy**: every domain row has `tenant_id UUID NOT NULL`. RLS policies enabled per schema with `SET LOCAL app.tenant_id = ...` set by request middleware.

---

## 6. Alembic Strategy

**Single Alembic env, multiple version branches (heads) per module** using branch labels.

```
alembic/
├── env.py                  # discovers metadata from all modules
└── versions/
    ├── auth/               # branch_labels=('auth',)
    ├── catalog/
    ├── stocks/
    └── ...
```

Workflow:
- `alembic revision --autogenerate --head=orders@head -m "add fbs items"` — scoped to one module.
- `alembic upgrade heads` — upgrades all branches.
- Module-local migration = module-local decision; no merge conflict when two devs add migrations in different modules.

---

## 7. Transactional Boundary

The **UnitOfWork** is the atomic unit:

```python
class UnitOfWork:
    def __init__(self, session: AsyncSession, bus: OutboxPublisher) -> None: ...

    async def __aenter__(self) -> "UnitOfWork":
        await self.session.begin()
        return self

    async def commit(self) -> None:
        await self.bus.flush_to_outbox(self.session)
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
```

Rules:
- HTTP endpoints: UoW spans the request.
- Arq jobs: UoW spans the job.
- Long-running syncs: **chunked transactions** — process 100 Uzum orders, commit, next chunk. Never hold a transaction across an HTTP call to Uzum.

---

## 8. Sync Worker (Arq) Design

### 8.1 Job catalog

| Job                        | Schedule | Priority | Retry           | Idempotency key                         |
|----------------------------|----------|----------|-----------------|-----------------------------------------|
| `sync_fbs_orders`          | 2 min    | high     | expo, max 6     | `sync:fbs:{integration_id}:{cursor}`    |
| `sync_fbs_status`          | 2 min    | high     | expo, max 6     | `sync:fbs_status:{integration_id}`      |
| `sync_fbo_sales`           | 10 min   | medium   | expo, max 5     | `sync:fbo:{integration_id}:{date}`      |
| `sync_stocks_fbo`          | 5 min    | medium   | expo, max 5     | `sync:stocks:{integration_id}`          |
| `sync_catalog`             | 60 min   | low      | expo, max 3     | `sync:catalog:{integration_id}`         |
| `sync_commissions_payouts` | 60 min   | low      | expo, max 3     | `sync:fin:{integration_id}:{period}`    |
| `outbox_relay`             | 1 sec    | critical | none (advisory) | `outbox:relay`                          |
| `rebuild_reports_daily`    | 03:00    | low      | none            | `reports:{tenant_id}:{date}`            |

### 8.2 Idempotency

Two layers:
- **Arq job-level**: `_job_id` set to idempotency key; duplicate enqueues are coalesced.
- **Domain-level**: Every Uzum record is written with UPSERT keyed by `(integration_id, external_id)`. Sync is always safe to replay.

### 8.3 Cursors

Each sync stores its cursor in `sync.cursors`. Cursor advances only on successful commit of a chunk.

### 8.4 Dead-letter queue

Failed job → row in `sync.dlq` with full request/response + exception. UI shows DLQ with retry button.

### 8.5 Priority

Arq queues split: `queue:high`, `queue:default`, `queue:low`. Three worker pools with different concurrency so slow catalog sync does not starve FBS polling.

---

## 9. Uzum Connector Integration

### 9.1 Client lifecycle

One `httpx.AsyncClient` per process (APP scope) with HTTP/2, connection pool. A `UzumClientFactory` produces per-integration clients that wrap this shared client with:
- auth header from `Connection.credentials` (encrypted at rest, decrypted on load using Fernet).
- rate limiter instance keyed by `integration_id`.
- retry policy.

### 9.2 Adaptive rate limiting

- Default: 5 rps, burst 10.
- On HTTP 429: halve rate, backoff with `Retry-After`, record event.
- On 100 consecutive successes: add 10% back, capped at observed max.
- Values persisted in `integrations.connection`.

### 9.3 Where it's called

Only from `sync` module's jobs and from `integrations` module's "test connection" endpoint. **Catalog/Orders/Stocks modules never touch `connectors/uzum` directly.** They receive already-normalized data via facade calls or read from their own tables populated by sync jobs.

---

## 10. Caching Strategy

| Purpose                    | Key pattern                                            | TTL       | Invalidation            |
|----------------------------|--------------------------------------------------------|-----------|-------------------------|
| Uzum catalog mirror cache  | `cache:uzum:catalog:{integration_id}:{sku}`            | 1h        | on `sync_catalog` end   |
| Aggregated reports         | `cache:report:{tenant_id}:{report}:{hash(params)}`     | 10m       | on `SaleCreated` event  |
| Uzum rate-limit counters   | `rl:uzum:{integration_id}` (token bucket, Lua)         | rolling   | n/a                     |
| Idempotency keys           | `idem:{scope}:{key}` → response hash                   | 24h       | n/a                     |
| Session/JWT revocation     | `jwt:revoked:{jti}`                                    | exp       | logout                  |
| Arq job locks              | `lock:{job_name}` via `SET NX EX`                      | job TTL   | on job end              |

`core/cache/keys.py` centralizes key builders. Reports use **cache-aside** with **stampede protection**.

---

## 11. Error Handling and Observability

### 11.1 Error model

```python
class AppError(Exception):
    code: str              # "stocks.insufficient"
    status: int            # HTTP
    message: str
    details: dict

class DomainError(AppError): ...      # 409/422
class NotFoundError(AppError): ...    # 404
class AuthError(AppError): ...        # 401/403
class IntegrationError(AppError):     # 502
    upstream: str
    upstream_status: int | None
class RateLimitedError(IntegrationError): ...
```

One FastAPI handler serializes to `application/problem+json` with `trace_id` and `correlation_id`.

### 11.2 Observability stack

- **structlog** + orjson renderer; every log has `tenant_id`, `correlation_id`, `user_id`, `integration_id`.
- **OpenTelemetry**: FastAPI, SQLAlchemy, httpx, redis, Arq auto-instrumented. 10% sampling, 100% on errors, 100% on Uzum calls.
- **Metrics**: Prometheus + business metrics (`uzum_requests_total`, `sync_lag_seconds`, `fbs_orders_in_status`).
- **Sentry**: PII/token scrubbing in `before_send`.
- **Correlation ID**: `X-Correlation-Id`, propagated to Uzum calls, carried into Arq jobs.

---

## 12. Testing Pyramid

- **Unit (70%)** — pure domain + application services with mocked repos. Fast, no DB.
- **Integration (20%)** — repository + Postgres (testcontainers), isolated schema per test run.
- **Contract tests for connectors (5%)** — `respx` cassettes under `tests/fixtures/uzum/`. Nightly CI against Uzum sandbox.
- **E2E / API (5%)** — `httpx.AsyncClient` against in-process FastAPI, DB reset per test.

CI stages: lint (ruff, mypy --strict on `domain/`), unit, integration, e2e, import-linter, alembic-check (autogenerate diff empty).

---

## 13. Deployment

### 13.1 Dev (docker-compose)

`postgres:16`, `redis:7`, `app` (Granian, hot reload), `worker-high`, `worker-default`, `worker-low`, `otel-collector`, `jaeger`, `mailhog`.

### 13.2 Prod (Kubernetes-ready)

- Single image, multiple Deployments: `api`, `worker-high`, `worker-default`, `worker-low`, `scheduler` (replicas=1, leader-elected via advisory lock).
- Liveness: `/health/live`. Readiness: `/health/ready` (DB + Redis ping + outbox backlog).
- HPA by CPU + p95 latency. Workers via KEDA Redis scaler (queue length).
- Secrets via sealed-secrets; Uzum tokens additionally Fernet-encrypted.
- DB: managed Postgres (Neon/RDS). PITR + daily snapshot.
- Blue-green migrations: **expand-contract**. `alembic upgrade heads` as pre-roll Job.

---

## 14. Risks and Trade-offs

1. **Shared DB session across facade calls** — modules look decoupled but transactional coupling is real. Treat facade methods as stable contracts from day 1; when extracting, every call becomes a saga step (budget two weeks per extraction).

2. **Polling Uzum inherently lags.** 2-min FBS poll + rate-limit backoff = 5-10 min on bad days. Mitigations: show `sync_lag_seconds` in UI, manual "sync now" button, inbox-shaped entry point so webhooks slot in painlessly.

3. **Multi-tenant noisy neighbor.** One tenant with 100k SKUs can saturate workers. Mitigation: per-tenant concurrency token, fair round-robin scheduler, circuit breaker on upstream errors.

---

## 15. Rules for Future Microservice Extraction

1. No cross-schema FKs (enforced).
2. Facades are the only public API — primitives in, DTOs out, idempotent mutations.
3. Cross-module reactions go through outbox, even in-process.
4. No shared domain models — each module owns its entities.
5. Per-module config and migrations.
6. Correlation ID + idempotency keys carried everywhere from day one.
7. No cross-module Arq job calls — if A enqueues, A handles; B subscribes to events.
8. Feature flags per module (per-tenant rollout ready).

Follow these and the monolith is a distributed system in disguise.
