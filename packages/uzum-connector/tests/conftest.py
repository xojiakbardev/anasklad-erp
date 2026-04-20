import pytest

from uzum_connector import ClientConfig, UzumClient


@pytest.fixture
def config() -> ClientConfig:
    return ClientConfig(
        token="test-token",
        base_url="https://api-seller.uzum.uz/api/seller-openapi",
        rate_per_second=1000,  # effectively disabled for tests
        rate_burst=1000,
        retry_attempts=1,
    )


@pytest.fixture
async def client(config: ClientConfig):
    async with UzumClient(config) as c:
        yield c
