from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    redis_host: str = Field(..., alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")

    es_schema: str = Field("http://", alias="ES_SCHEMA")
    es_host: str = Field(..., alias="ES_HOST")
    es_port: int = Field(9200, alias="ES_PORT")
    es_movies_index_name: str = Field("movies", alias="MOVIES_INDEX_NAME")
    es_persons_index_name: str = Field("persons", alias="PERSONS_INDEX_NAME")
    es_genres_index_name: str = Field("genres", alias="GENRES_INDEX_NAME")

    service_url: str = Field("http://fastapi:8000", alias="SERVICE_URL")

    test_data_amount: int = 200

    @property
    def elastic_dsn(self) -> str:
        return f"{self.es_schema}{self.es_host}:{self.es_port}"

    @property
    def redis_dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"


test_settings = TestSettings()
