import pytest

from tests.functional.testdata.films import films


@pytest.fixture(scope="session")
def films_data():
    films[0]["imdb_rating"] = 0.0
    films[-1]["imdb_rating"] = 10.0
    return films