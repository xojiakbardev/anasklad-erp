"""
UzumClient — the public face of the connector.

Usage:
    async with UzumClient(ClientConfig(token="...")) as client:
        shops = await client.list_shops()
        products = await client.list_products(shop_id=shops[0].id, size=50, page=0)
"""
from __future__ import annotations

import asyncio
import logging
from types import TracebackType
from typing import Any, Self

import httpx
import orjson
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from uzum_connector.config import ClientConfig
from uzum_connector.errors import (
    UzumAuthError,
    UzumError,
    UzumNotFoundError,
    UzumRateLimitError,
    UzumServerError,
    UzumTransportError,
    UzumValidationError,
)
from uzum_connector.models import (
    FbsOrder,
    FbsOrderScheme,
    FbsOrderStatus,
    FbsOrdersPage,
    GenericResponse,
    Product,
    ProductsPage,
    Shop,
)
from uzum_connector.rate_limit import (
    AdaptiveRateAdjuster,
    InMemoryTokenBucket,
    NoopRateLimiter,
    RateLimiter,
)

logger = logging.getLogger("uzum_connector")

_RETRYABLE = (UzumRateLimitError, UzumServerError, UzumTransportError)


class UzumClient:
    """
    Async HTTP client for the Uzum Market Seller OpenAPI.

    - Connection-pooled httpx (HTTP/2 by default)
    - Token-bucket rate limiter (adaptive on 429)
    - Exponential-backoff retry on 429/5xx/network errors
    - Strict pydantic DTOs for all responses
    - Safe to share across asyncio tasks
    """

    def __init__(
        self,
        config: ClientConfig,
        *,
        http_client: httpx.AsyncClient | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self._config = config
        self._owns_client = http_client is None
        self._http = http_client or self._build_http_client(config)

        if rate_limiter is None:
            bucket = InMemoryTokenBucket(config.rate_per_second, config.rate_burst)
            self._bucket = bucket
            self._adjuster: AdaptiveRateAdjuster | None = AdaptiveRateAdjuster(bucket)
            self._limiter: RateLimiter = bucket
        else:
            self._bucket = None
            self._adjuster = None
            self._limiter = rate_limiter

    # ---- lifecycle ----

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    @staticmethod
    def _build_http_client(c: ClientConfig) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=c.base_url,
            http2=c.http2,
            timeout=httpx.Timeout(
                connect=c.connect_timeout,
                read=c.read_timeout,
                write=c.write_timeout,
                pool=c.pool_timeout,
            ),
            limits=httpx.Limits(
                max_connections=c.max_connections,
                max_keepalive_connections=c.max_keepalive_connections,
            ),
            headers={
                "Authorization": c.token,  # Uzum: no "Bearer " prefix
                "Accept": "application/json",
                "User-Agent": c.user_agent,
            },
        )

    # ---- observability ----

    @property
    def current_rate(self) -> float | None:
        return self._adjuster.current_rate if self._adjuster else None

    # ---- endpoints ----

    async def list_shops(self) -> list[Shop]:
        """GET /v1/shops — seller's own shops."""
        data = await self._request("GET", "/v1/shops")
        # Response: raw array of OrganizationDto (no envelope)
        if isinstance(data, list):
            return [Shop.model_validate(item) for item in data]
        # Some deployments wrap it — be defensive
        resp = GenericResponse[list[Shop]].model_validate(data)
        return resp.payload or []

    async def list_products(
        self,
        shop_id: int,
        *,
        size: int = 50,
        page: int = 0,
        search_query: str | None = None,
        sort_by: str = "DEFAULT",
        order: str = "ASC",
        filter_: str = "ALL",
        product_rank: str | None = None,
    ) -> ProductsPage:
        """GET /v1/product/shop/{shopId}"""
        params: dict[str, Any] = {
            "size": size,
            "page": page,
            "sortBy": sort_by,
            "order": order,
            "filter": filter_,
        }
        if search_query:
            params["searchQuery"] = search_query
        if product_rank:
            params["productRank"] = product_rank

        data = await self._request("GET", f"/v1/product/shop/{shop_id}", params=params)
        return ProductsPage.model_validate(data)

    async def get_product(self, shop_id: int, product_id: int) -> Product | None:
        """Convenience: search a single product within a shop."""
        page = await self.list_products(shop_id=shop_id, size=1, page=0)
        for p in page.product_list:
            if p.product_id == product_id:
                return p
        return None

    async def list_fbs_orders(
        self,
        shop_ids: list[int],
        *,
        status: FbsOrderStatus | None = None,
        scheme: FbsOrderScheme | None = None,
        date_from_ms: int | None = None,
        date_to_ms: int | None = None,
        page: int = 0,
        size: int = 20,
    ) -> FbsOrdersPage:
        """GET /v2/fbs/orders"""
        if not shop_ids:
            raise ValueError("shop_ids must not be empty")
        params: dict[str, Any] = {
            "shopIds": shop_ids,
            "page": page,
            "size": size,
        }
        if status is not None:
            params["status"] = status.value
        if scheme is not None:
            params["scheme"] = scheme.value
        if date_from_ms is not None:
            params["dateFrom"] = date_from_ms
        if date_to_ms is not None:
            params["dateTo"] = date_to_ms

        data = await self._request("GET", "/v2/fbs/orders", params=params)
        resp = GenericResponse[FbsOrdersPage].model_validate(data)
        if not resp.is_ok or resp.payload is None:
            raise self._error_from_envelope(resp, status_code=200)
        return resp.payload

    async def get_fbs_order(self, order_id: int) -> FbsOrder:
        """GET /v1/fbs/order/{orderId}"""
        data = await self._request("GET", f"/v1/fbs/order/{order_id}")
        resp = GenericResponse[FbsOrder].model_validate(data)
        if not resp.is_ok or resp.payload is None:
            raise self._error_from_envelope(resp, status_code=200)
        return resp.payload

    async def confirm_fbs_order(self, order_id: int) -> FbsOrder:
        """POST /v1/fbs/order/{orderId}/confirm"""
        data = await self._request("POST", f"/v1/fbs/order/{order_id}/confirm")
        resp = GenericResponse[FbsOrder].model_validate(data)
        if not resp.is_ok or resp.payload is None:
            raise self._error_from_envelope(resp, status_code=200)
        return resp.payload

    async def cancel_fbs_order(
        self, order_id: int, *, reason: str, comment: str | None = None
    ) -> None:
        """POST /v1/fbs/order/{orderId}/cancel"""
        body: dict[str, Any] = {"reason": reason}
        if comment:
            body["comment"] = comment
        await self._request("POST", f"/v1/fbs/order/{order_id}/cancel", json=body)

    async def get_fbs_order_label(self, order_id: int, *, size: str = "LARGE") -> bytes:
        """GET /v1/fbs/order/{orderId}/labels/print → base64-decoded PDF bytes."""
        import base64

        data = await self._request(
            "GET", f"/v1/fbs/order/{order_id}/labels/print", params={"size": size}
        )
        if not isinstance(data, dict):
            raise ValueError("unexpected label response shape")
        payload = data.get("payload") or {}
        documents = payload.get("document") or []
        if not documents:
            raise ValueError("label service returned no document")
        return base64.b64decode(documents[0])

    async def iter_fbs_orders(
        self,
        shop_ids: list[int],
        *,
        status: FbsOrderStatus | None = None,
        page_size: int = 50,
        **kw: Any,
    ) -> list[FbsOrder]:
        """Convenience: paginate through all FBS orders matching filters."""
        all_orders: list[FbsOrder] = []
        page = 0
        while True:
            result = await self.list_fbs_orders(
                shop_ids, status=status, page=page, size=page_size, **kw
            )
            all_orders.extend(result.orders)
            if len(result.orders) < page_size:
                break
            page += 1
            if page > 1000:  # safety
                break
        return all_orders

    # ---- core request plumbing ----

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._config.retry_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self._config.retry_min_wait,
                max=self._config.retry_max_wait,
            ),
            retry=retry_if_exception_type(_RETRYABLE),
            reraise=True,
        ):
            with attempt:
                return await self._do_request(method, path, params=params, json=json)
        return None  # unreachable — reraise=True

    async def _do_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None,
        json: dict[str, Any] | None,
    ) -> Any:
        await self._limiter.acquire()

        try:
            response = await self._http.request(
                method,
                path,
                params=params,
                content=orjson.dumps(json) if json is not None else None,
                headers={"Content-Type": "application/json"} if json is not None else None,
            )
        except (httpx.TimeoutException, httpx.TransportError) as e:
            raise UzumTransportError(f"transport error: {e}") from e

        correlation_id = response.headers.get("x-trace-id") or response.headers.get("trace-id")

        if response.status_code == 429:
            if self._adjuster:
                self._adjuster.record_429()
            retry_after = _parse_retry_after(response.headers.get("retry-after"))
            raise UzumRateLimitError(
                "rate limited by Uzum",
                status_code=429,
                retry_after_seconds=retry_after,
                correlation_id=correlation_id,
            )

        if 500 <= response.status_code < 600:
            raise UzumServerError(
                f"server error {response.status_code}",
                status_code=response.status_code,
                correlation_id=correlation_id,
            )

        if response.status_code == 401:
            raise UzumAuthError(
                "token invalid or expired",
                status_code=401,
                correlation_id=correlation_id,
            )
        if response.status_code == 403:
            raise UzumAuthError(
                "forbidden — token lacks required scope",
                status_code=403,
                correlation_id=correlation_id,
            )
        if response.status_code == 404:
            raise UzumNotFoundError(
                "resource not found",
                status_code=404,
                correlation_id=correlation_id,
            )
        if response.status_code == 400:
            payload = _safe_json(response)
            raise UzumValidationError(
                _extract_message(payload, "validation error"),
                status_code=400,
                code=_extract_code(payload),
                payload=payload,
                correlation_id=correlation_id,
            )
        if not 200 <= response.status_code < 300:
            payload = _safe_json(response)
            raise UzumError(
                _extract_message(payload, f"unexpected status {response.status_code}"),
                status_code=response.status_code,
                code=_extract_code(payload),
                payload=payload,
                correlation_id=correlation_id,
            )

        if self._adjuster:
            self._adjuster.record_success()

        if not response.content:
            return None
        return _safe_json(response)

    def _error_from_envelope(
        self, resp: GenericResponse[Any], *, status_code: int
    ) -> UzumError:
        if resp.errors:
            first = resp.errors[0]
            return UzumError(
                first.message,
                status_code=status_code,
                code=first.code,
                payload=first.payload,
            )
        return UzumError("unknown error in envelope", status_code=status_code)


# ---- helpers ----


def _safe_json(response: httpx.Response) -> Any:
    try:
        return orjson.loads(response.content)
    except orjson.JSONDecodeError:
        return {"raw": response.text}


def _extract_message(payload: Any, default: str) -> str:
    if isinstance(payload, dict):
        errors = payload.get("errors")
        if errors and isinstance(errors, list) and isinstance(errors[0], dict):
            return str(errors[0].get("message") or default)
        if payload.get("error"):
            return str(payload["error"])
    return default


def _extract_code(payload: Any) -> str | None:
    if isinstance(payload, dict):
        errors = payload.get("errors")
        if errors and isinstance(errors, list) and isinstance(errors[0], dict):
            return errors[0].get("code")
    return None


def _parse_retry_after(header: str | None) -> float | None:
    if not header:
        return None
    try:
        return float(header)
    except ValueError:
        return None
