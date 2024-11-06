import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from tests.functional.settings import test_settings
from tests.functional.utils import Utilities as U


@pytest_asyncio.fixture(
    name="es_client", loop_scope="session", scope="session"
)
async def es_client():
    es_client = AsyncElasticsearch(test_settings.elastic_dsn)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(
    name="redis_client", loop_scope="session", scope="session"
)
async def redis_client():
    redis_client = Redis(
        host=test_settings.redis_host, port=test_settings.redis_port
    )
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture(name="clear_cache", loop_scope="session")
async def clear_cache(redis_client: Redis):
    await redis_client.flushdb()


@pytest_asyncio.fixture(name="es_write_data", loop_scope="session")
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(
        index_name: str, index: dict, id_field_name: str, data: list[dict]
    ):
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(
            index=index_name,
            body=index,
        )

        query = U.transform_data_to_es_format(index_name, id_field_name, data)
        updated, errors = await async_bulk(
            client=es_client, actions=query, refresh=True
        )

        if errors:
            raise Exception("Ошибка записи данных в Elasticsearch")

    return inner
