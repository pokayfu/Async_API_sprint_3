import uuid

from tests.functional.settings import test_settings

from .films import films

persons = [
    {
        "person_id": str(uuid.uuid4()),
        "full_name": "Carrie Fisher",
        "films": [{"id": film["id"], "roles": ["actor"]} for film in films],
    }
    for _ in range(test_settings.test_data_amount)
]
