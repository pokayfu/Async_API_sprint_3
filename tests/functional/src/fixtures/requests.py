import aiohttp
import pytest_asyncio

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(name="make_get_request", loop_scope="session")
def make_get_request():
    async def inner(url_path: str, query_data: dict | None = None):
        async with aiohttp.ClientSession() as session:
            url = test_settings.service_url + url_path
            async with session.get(url, params=query_data) as response:
                status = response.status
                body = await response.json()
        return status, body

    return inner
