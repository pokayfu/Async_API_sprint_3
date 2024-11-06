import pytest

from tests.functional.testdata.genres import genres


@pytest.fixture(scope="session")
def genres_data():
    return genres
