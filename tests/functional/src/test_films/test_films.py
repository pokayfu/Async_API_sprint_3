from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.es_schemes.movies_index import movies_index


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"page_size": 60, "page": 1}, {"status": HTTPStatus.OK, "length": 60}),
        ({"page_size": 25, "page": 1}, {"status": HTTPStatus.OK, "length": 25}),
        ({"page_size": 1, "page": 1}, {"status": HTTPStatus.OK, "length": 1}),
        ({"page_size": 100, "page": 1}, {"status": HTTPStatus.OK, "length": 100}),
        ({}, {"status": HTTPStatus.OK, "length": 10}),
        ({"page_size": 75, "page": 3}, {"status": HTTPStatus.OK, "length": 50}),
    ],
)
@pytest.mark.asyncio
async def test_films_pagination(
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
    status, body = await make_get_request("/api/v1/films/", query_data)

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
        ({"sort": 75}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
        ({"sort": "qwe"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_films_validation(
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
    status, body = await make_get_request("/api/v1/films/", query_data)

    assert status == expected_answer["status"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"sort": "-imdb_rating"}, {"status": HTTPStatus.OK, "rating": 10.0}),
        ({"sort": "imdb_rating"}, {"status": HTTPStatus.OK, "rating": 0.0}),
    ],
)
@pytest.mark.asyncio
async def test_films_sorting(
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
    status, body = await make_get_request("/api/v1/films/", query_data)

    assert status == expected_answer["status"]
    assert body[0]["imdb_rating"] == expected_answer["rating"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"genre": "Comedy"}, {"status": HTTPStatus.OK, "length": 0}),
        ({"genre": "Action"}, {"status": HTTPStatus.OK, "length": 10}),
    ],
)
@pytest.mark.asyncio
async def test_films_genre_filtering(
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
    status, body = await make_get_request("/api/v1/films/", query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.asyncio
async def test_film_by_id(
        films_data,
        make_get_request,
        es_write_data,
        clear_cache,
):
    await es_write_data(
        index_name=test_settings.es_movies_index_name,
        index=movies_index,
        id_field_name="id",
        data=films_data,
    )

    film_id = films_data[0]["id"]
    status, body = await make_get_request(f"/api/v1/films/{film_id}")
    assert film_id == body["id"]
    assert status == HTTPStatus.OK
