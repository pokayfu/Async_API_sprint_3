import asyncio
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from file_api.src.db.pg import get_db_session
from file_api.src.db.minio import set_minio, get_minio
from file_api.src.main import app
from file_api.src.services.files import FileService
from miniopy_async import Minio
from httpx import AsyncClient


@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest_asyncio.fixture(name='mock_minio', scope='session')
async def fixture_mock_minio():
    client = MagicMock(spec=Minio)
    client.get_object = AsyncMock()
    client.get_presigned_url = AsyncMock()
    client.put_object = AsyncMock()
    client.close = AsyncMock()
    set_minio(client)
    yield client
    await client.close()


@pytest_asyncio.fixture(name='mock_pg_session', scope='session')
async def fixture_mock_pg_session():
    session = MagicMock(spec=AsyncSession)
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='file_service')
def fixture_file_service(mock_minio, mock_pg_session):
    return FileService(mock_minio, mock_pg_session)


@pytest_asyncio.fixture(name='mock_file')
def fixture_mock_file():
    file = MagicMock(spec=UploadFile)
    file.filename = 'test.txt'
    file.content_type = 'text/plain'
    file.read = AsyncMock(return_value=b"test content")
    file.seek = AsyncMock()
    file.file = MagicMock()
    return file


@pytest_asyncio.fixture(name='async_client', scope='session')
async def fixture_async_client():
    async with AsyncClient(app=app, base_url='http://localhost/api/v1/files/') as client:
        yield client


@pytest_asyncio.fixture(name='refresh_clients_sessions', scope='session')
def fixture_refresh_clients_sessions(mock_pg_session, mock_minio):
    app.dependency_overrides[get_db_session] =  lambda: (mock_pg_session)
    app.dependency_overrides[get_minio] = lambda: mock_minio
    yield
    app.dependency_overrides = {}

