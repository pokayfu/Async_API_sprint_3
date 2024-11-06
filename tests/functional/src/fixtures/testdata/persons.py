import pytest

from tests.functional.testdata.persons import persons


@pytest.fixture(scope="session")
def persons_data():
    return persons
