import os
from logging import config as logging_config
from pydantic import  Field
from src.core.logger import LOGGING
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class PostgresSettings(BaseSettings):
    db: str = Field(alias='DB_NAME')
    user: str = Field(alias='DB_USER')
    password: str = Field(alias='DB_PASSWORD')
    host: str = Field(alias='DB_HOST')
    port: str = Field(alias='DB_PORT')

    @property
    def url(self):
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'


class MinIOSettings(BaseSettings):
    minio_host: str = Field(default='0.0.0.0', env='MINIO_HOST')
    minio_port: int = Field(default=9000, env='MINIO_PORT')
    minio_root_user: str = Field(default='practicum', env='MINIO_ROOT_USER')
    minio_root_password: str = Field(default='StrongPass', env='MINIO_ROOT_PASSWORD')
    backet_name: str = Field(default='movies', env='BACKET_NAME')
    secure_connection:bool = Field(default=False, env='SECURE_CONNECTION') == 'True' 

class AppSettings(BaseSettings):
    project_name: str = Field(default='File API', env='File API')
    uvicorn_host: str = Field(default='localhost', env='FILE_API_UVICORN_HOST')
    uvicorn_port: int = Field(default=8081, env='FILE_API_UVICORN_PORT')


pg_settings: PostgresSettings = PostgresSettings()
app_settings:AppSettings = AppSettings()
minio_settings: MinIOSettings = MinIOSettings()


logging_config.dictConfig(LOGGING)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))