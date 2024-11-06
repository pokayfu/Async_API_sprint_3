import os
from logging import config as logging_config
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.logger import LOGGING
from dotenv import load_dotenv
load_dotenv()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    project_name: str = Field("movies", alias="PROJECT_NAME")
    redis_host: str = Field(..., alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    es_schema: str = Field("http://", alias="ES_SCHEMA")
    es_host: str = Field(..., alias="ES_HOST")
    es_port: int = Field(9200, alias="ES_PORT")
    movies_index_name: str = Field("movies", alias="MOVIES_INDEX_NAME")
    genres_index_name: str = Field("genres", alias="GENRES_INDEX_NAME")
    persons_index_name: str = Field("persons", alias="PERSONS_INDEX_NAME")
    base_dir: str = Field(BASE_DIR, alias="BASE_DIR")
    cache_expire_in_seconds: int = Field(
        60 * 5, alias="CACHE_EXPIRE_IN_SECONDS"
    )


settings = Settings()
