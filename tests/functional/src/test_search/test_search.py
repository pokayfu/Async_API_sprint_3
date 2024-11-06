from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.es_schemes.movies_index import movies_index
from tests.functional.testdata.es_schemes.persons_index import persons_index


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "The Star"}, {"status": HTTPStatus.OK, "length": 10}),
        ({"query": "Mashed potato"}, {"status": HTTPStatus.OK, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_films_search(
    films_data,
    make_get_request,
    es_write_data,
    clear_cache,
    query_data: dict,
    expected_answer: dict,
):
    await es_write_data(
        index_name=test_settings.es_movies_index_name,
        index=movies_index,
        id_field_name="id",
        data=films_data,
    )
    status, body = await make_get_request("/api/v1/films/search/", query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "Carrie Fisher"}, {"status": HTTPStatus.OK, "length": 10}),
        ({"query": "Harry Potter"}, {"status": HTTPStatus.OK, "length": 0}),
    ],
)
@pytest.mark.asyncio
async def test_persons_search(
    persons_data,
    make_get_request,
    es_write_data,
    clear_cache,
    query_data: dict,
    expected_answer: dict,
):
    await es_write_data(
        index_name=test_settings.es_persons_index_name,
        index=persons_index,
        id_field_name="person_id",
        data=persons_data,
    )
    status, body = await make_get_request(
        "/api/v1/persons/search/", query_data
    )

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_length",
    [
        ({"query": "Star"}, 10),
        ({"query": "Unknown"}, 0),
    ],
)
@pytest.mark.asyncio
async def test_films_partial_search(
    films_data,
    make_get_request,
    es_write_data,
    clear_cache,
    query_data: dict,
    expected_length: int,
):
    await es_write_data(
        index_name=test_settings.es_movies_index_name,
        index=movies_index,
        id_field_name="id",
        data=films_data,
    )
    status, body = await make_get_request("/api/v1/films/search/", query_data)

    assert status == HTTPStatus.OK
    assert len(body) == expected_length

