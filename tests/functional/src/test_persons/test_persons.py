from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.es_schemes.persons_index import persons_index


@pytest.mark.asyncio
async def test_person_film(
    persons_data,
    make_get_request,
    es_write_data,
    clear_cache,
):
    await es_write_data(
        index_name=test_settings.es_persons_index_name,
        index=persons_index,
        id_field_name="person_id",
        data=persons_data,
    )
    film_id = persons_data[0]["films"][0]["id"]
    person_id = persons_data[0]["person_id"]
    status, body = await make_get_request(f"/api/v1/persons/{person_id}/film")

    assert status == HTTPStatus.OK
    assert film_id == body[0]["id"]


@pytest.mark.asyncio
async def test_person_by_id(
    persons_data,
    make_get_request,
    es_write_data,
    clear_cache,
):
    await es_write_data(
        index_name=test_settings.es_persons_index_name,
        index=persons_index,
        id_field_name="person_id",
        data=persons_data,
    )
    person_id = persons_data[0]["person_id"]
    status, body = await make_get_request(f"/api/v1/persons/{person_id}")

    assert status == HTTPStatus.OK
    assert person_id == body["person_id"]


@pytest.mark.asyncio
async def test_person_film_not_found(
    make_get_request,
    clear_cache,
):
    status, body = await make_get_request("/api/v1/persons/non_existent_id/film")
    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_person_not_found(
    make_get_request,
    clear_cache,
):
    status, body = await make_get_request("/api/v1/persons/non_existent_id")
    assert status == HTTPStatus.NOT_FOUND

