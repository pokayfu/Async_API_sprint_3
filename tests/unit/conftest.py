from unittest.mock import AsyncMock, MagicMock

import pytest_asyncio
from fastapi import FastAPI, UploadFile
from httpx import AsyncClient
from miniopy_async import Minio
from sqlalchemy.ext.asyncio import AsyncSession
from file_api.src.db.pg import get_db_session
from file_api.src.db.minio import get_minio
from file_api.src.services.files import FileService
from file_api.src.main import app as fastapi_app


@pytest_asyncio.fixture(scope="session")
async def mock_minio_client():
    """
    Асинхронный мок MinIO клиента.
    """
    client = MagicMock(spec=Minio)
    client.put_object = AsyncMock()
    client.get_object = AsyncMock()
    client.get_presigned_url = AsyncMock()
    client.stat_object = AsyncMock()
    client.remove_object = AsyncMock()
    client.close = AsyncMock()
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="session")
async def mock_db_session():
    """
    Асинхронный мок сессии базы данных.
    """
    session = MagicMock(spec=AsyncSession)
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.delete = AsyncMock()
    yield session
    await session.close()


@pytest_asyncio.fixture
def test_file():
    """
    Мок файла для тестирования.
    """
    file = MagicMock(spec=UploadFile)
    file.filename = "test.txt"
    file.content_type = "text/plain"
    file.read = AsyncMock(return_value=b"test content")
    file.seek = AsyncMock()
    file.file = MagicMock()
    return file


@pytest_asyncio.fixture(scope="function")
async def file_service(mock_minio_client, mock_db_session):
    """
    Инстанс FileService с асинхронными моками для MinIO и базы данных.
    """
    yield FileService(minio=mock_minio_client, db_session=mock_db_session)



@pytest_asyncio.fixture(scope="session")
def app() -> FastAPI:
    """
    Фикстура для предоставления экземпляра приложения FastAPI.
    """
    return fastapi_app


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """
    фикстура для создания клиента AsyncClient.
    Поддерживает динамическую настройку приложения и базового URL.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://localhost/api/v1/files") as client:
        yield client


@pytest_asyncio.fixture(name="override_dependencies", scope="session")
def fixture_override_dependencies(mock_db_session, mock_minio_client):
    """
    Подменяет зависимости приложения FastAPI для изолированного тестирования.
    """
    fastapi_app.dependency_overrides[get_db_session] = lambda: mock_db_session
    fastapi_app.dependency_overrides[get_minio] = lambda: mock_minio_client
    yield
    fastapi_app.dependency_overrides = {}