from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.es_schemes.genres_index import genres_index


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"page_size": 10, "page": 1}, {"status": HTTPStatus.OK, "length": 10}),
        ({"page_size": 27, "page": 1}, {"status": HTTPStatus.OK, "length": 26}),
        ({"page_size": 1, "page": 1}, {"status": HTTPStatus.OK, "length": 1}),
        ({"page_size": 100, "page": 1}, {"status": HTTPStatus.OK, "length": 26}),
        ({}, {"status": HTTPStatus.OK, "length": 10}),
        ({"page_size": 10, "page": 4}, {"status": HTTPStatus.OK, "length": 0}),
        ({"page_size": 10, "page": 3}, {"status": HTTPStatus.OK, "length": 6}),
    ],
)
@pytest.mark.asyncio
async def test_genres_pagination(
    genres_data,
    make_get_request,
    es_write_data,
    clear_cache,
    query_data: dict,
    expected_answer: dict,
):
    await es_write_data(
        index_name=test_settings.es_genres_index_name,
        index=genres_index,
        id_field_name="id",
        data=genres_data,
    )
    status, body = await make_get_request("/api/v1/genres/", query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"page_size": "qwe"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"page_size": 0}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"page_size": -5}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"page_size": 101}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"page": "qwe"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"page": 0}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"page": -5}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_genres_validation(
    genres_data,
    make_get_request,
    es_write_data,
    clear_cache,
    query_data: dict,
    expected_answer: dict,
):
    await es_write_data(
        index_name=test_settings.es_genres_index_name,
        index=genres_index,
        id_field_name="id",
        data=genres_data,
    )
    status, body = await make_get_request("/api/v1/genres/", query_data)

    assert status == expected_answer["status"]


@pytest.mark.asyncio
async def test_genre_by_id(
    genres_data,
    make_get_request,
    es_write_data,
    clear_cache,
):
    await es_write_data(
        index_name=test_settings.es_genres_index_name,
        index=genres_index,
        id_field_name="id",
        data=genres_data,
    )
    genre_id = genres_data[0]["id"]
    status, body = await make_get_request(f"/api/v1/genres/{genre_id}")

    assert genre_id == body["id"]


@pytest.mark.asyncio
async def test_genre_not_found(
    make_get_request,
    clear_cache,
):
    status, body = await make_get_request("/api/v1/genres/non_existent_id")
    assert status == HTTPStatus.NOT_FOUND
