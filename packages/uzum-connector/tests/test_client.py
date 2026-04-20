import httpx
import pytest
import respx

from uzum_connector import (
    ClientConfig,
    UzumAuthError,
    UzumClient,
    UzumRateLimitError,
    UzumServerError,
    UzumValidationError,
)
from uzum_connector.models import FbsOrderScheme, FbsOrderStatus


BASE = "https://api-seller.uzum.uz/api/seller-openapi"


@respx.mock
async def test_list_shops_ok(client: UzumClient):
    respx.get(f"{BASE}/v1/shops").mock(
        return_value=httpx.Response(200, json=[{"id": 101, "name": "MyShop"}])
    )
    shops = await client.list_shops()
    assert len(shops) == 1
    assert shops[0].id == 101
    assert shops[0].name == "MyShop"


@respx.mock
async def test_list_shops_invalid_token(client: UzumClient):
    respx.get(f"{BASE}/v1/shops").mock(return_value=httpx.Response(401))
    with pytest.raises(UzumAuthError):
        await client.list_shops()


@respx.mock
async def test_list_products_parses_sku_fields(client: UzumClient):
    payload = {
        "productList": [
            {
                "productId": 55,
                "title": "Ko'ylak",
                "quantityActive": 10,
                "quantityFbs": 3,
                "skuList": [
                    {
                        "skuId": 901,
                        "skuTitle": "M/Red",
                        "quantityActive": 5,
                        "quantityFbs": 2,
                        "price": 150000,
                        "purchasePrice": 80000,
                        "barcode": 4601234567890,
                    }
                ],
            }
        ],
        "totalProductsAmount": 1,
    }
    respx.get(f"{BASE}/v1/product/shop/101").mock(return_value=httpx.Response(200, json=payload))

    page = await client.list_products(shop_id=101, size=50, page=0)
    assert page.total == 1
    assert page.product_list[0].product_id == 55
    sku = page.product_list[0].sku_list[0]
    assert sku.sku_id == 901
    assert sku.quantity_fbs == 2
    assert sku.price == 150000


@respx.mock
async def test_list_fbs_orders_parses_status(client: UzumClient):
    payload = {
        "payload": {
            "orders": [
                {
                    "id": 777,
                    "status": "CREATED",
                    "scheme": "FBS",
                    "shopId": 101,
                    "price": 250000,
                    "orderItems": [],
                }
            ],
            "totalAmount": 1,
        },
        "errors": [],
    }
    respx.get(f"{BASE}/v2/fbs/orders").mock(return_value=httpx.Response(200, json=payload))

    result = await client.list_fbs_orders(
        shop_ids=[101], status=FbsOrderStatus.CREATED, scheme=FbsOrderScheme.FBS
    )
    assert result.total == 1
    assert result.orders[0].id == 777
    assert result.orders[0].status is FbsOrderStatus.CREATED
    assert result.orders[0].scheme is FbsOrderScheme.FBS


@respx.mock
async def test_rate_limit_raises_with_retry_after():
    # Use a config with 0 retries so the error surfaces immediately
    cfg = ClientConfig(token="t", rate_per_second=1000, rate_burst=1000, retry_attempts=1)
    async with UzumClient(cfg) as c:
        respx.get(f"{BASE}/v1/shops").mock(
            return_value=httpx.Response(429, headers={"retry-after": "2"})
        )
        with pytest.raises(UzumRateLimitError) as exc:
            await c.list_shops()
        assert exc.value.retry_after_seconds == 2.0


@respx.mock
async def test_server_error_retries_then_gives_up():
    cfg = ClientConfig(
        token="t", rate_per_second=1000, rate_burst=1000,
        retry_attempts=2, retry_min_wait=0.01, retry_max_wait=0.02,
    )
    async with UzumClient(cfg) as c:
        route = respx.get(f"{BASE}/v1/shops").mock(return_value=httpx.Response(503))
        with pytest.raises(UzumServerError):
            await c.list_shops()
        assert route.call_count == 2


@respx.mock
async def test_validation_error_not_retried():
    cfg = ClientConfig(
        token="t", rate_per_second=1000, rate_burst=1000,
        retry_attempts=5, retry_min_wait=0.01,
    )
    async with UzumClient(cfg) as c:
        route = respx.get(f"{BASE}/v1/shops").mock(
            return_value=httpx.Response(400, json={"errors": [{"code": "X", "message": "bad"}]})
        )
        with pytest.raises(UzumValidationError) as exc:
            await c.list_shops()
        assert exc.value.code == "X"
        assert route.call_count == 1
