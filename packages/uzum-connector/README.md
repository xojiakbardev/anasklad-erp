# uzum-connector

Async Python client for the Uzum Market Seller OpenAPI.

> Standalone package. Does NOT depend on Anasklad domain code.
> Can be open-sourced independently in the future.

## Status

🚧 Skeleton — implementation starts in Sprint 1.

## Scope

- Auth via `Authorization: <token>` header
- Adaptive token-bucket rate limiting
- Retry with exponential backoff (tenacity)
- HTTP/2 + connection pooling (httpx)
- Pydantic DTOs mirroring Uzum schema
- Covered endpoints (Sprint 1):
  - `GET /v1/shops`
  - `GET /v1/product/shop/{shopId}`
  - `GET /v2/fbs/orders`
- Covered endpoints (Sprint 3+): all Product, Order, Invoice, Finance, FBS Invoice endpoints

## Install

```bash
uv pip install -e packages/uzum-connector
```
