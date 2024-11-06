import pytest
from pytest_asyncio import is_async_test

from .fixtures.db import clear_cache, es_client, es_write_data, redis_client
from .fixtures.requests import make_get_request
from .fixtures.testdata.films import films_data
from .fixtures.testdata.genres import genres_data
from .fixtures.testdata.persons import persons_data


def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)
