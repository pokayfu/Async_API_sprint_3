from file_api.src.models.file_db import FileDbModel
from unittest.mock import AsyncMock, MagicMock
from aiohttp import ClientResponse, StreamReader
from starlette.responses import StreamingResponse
from file_api.src.utils.exceptions import NotFoundException
import pytest


short_name = 'test_short_uuid'
path_in_storage = 'test/path'
filename = 'test.txt'
content = b'test content'
mock_presigned_url = 'http://presigned.url'
path = 'test/path'


@pytest.mark.anyio
async def test_download_file_success(mock_pg_session, mock_minio,
                                     async_client, refresh_clients_sessions):
    mock_file_record = FileDbModel(
        path_in_storage=path_in_storage,
        filename=filename,
        short_name=short_name,
        size=123,
        file_type='text/plain'
    )
    mock_pg_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=mock_file_record)

    async def mock_iter_chunked(chunk_size):
        yield content

    mock_response = MagicMock(ClientResponse)
    mock_response.content = MagicMock(StreamReader)
    mock_response.content.iter_chunked = mock_iter_chunked
    mock_minio.get_object.return_value = mock_response
    response = await async_client.get(f'/download/{short_name}')
    response_content = await response.aread()
    assert response.status_code == 200
    assert response_content == content
    assert response.headers['content-disposition'] == f'filename="{filename}"'


@pytest.mark.anyio
async def test_download_file_not_found(mock_pg_session, async_client, refresh_clients_sessions):
    mock_pg_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)
    response = await async_client.get(f'/download/{short_name}')
    print(response)
    assert response.status_code == 404
    assert response.json() == {'detail': 'File not found'}

@pytest.mark.anyio
async def test_get_file_record_not_found(file_service, mock_pg_session):
    mock_pg_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)
    with pytest.raises(NotFoundException) as e:
        await file_service.get_file_record(short_name)
    assert e.value.detail == 'File not found'


@pytest.mark.anyio
async def test_get_file(file_service, mock_minio):
    mock_response = MagicMock(ClientResponse)
    mock_response.content = MagicMock(StreamReader)
    mock_response.content.iter_chunked = AsyncMock(return_value=[content])
    mock_minio.get_object.return_value = mock_response
    response = await file_service.get_file(path, filename)
    assert isinstance(response, StreamingResponse)


@pytest.mark.anyio
async def test_get_presigned_url(file_service, mock_pg_session, mock_minio):
    mock_minio.get_presigned_url.return_value = mock_presigned_url
    presigned_url = await file_service.get_presigned_url(short_name)
    assert presigned_url == mock_presigned_url


@pytest.mark.anyio
async def test_get_presigned_url_success(mock_pg_session, mock_minio,
                                         async_client, refresh_clients_sessions):
    mock_file_record = FileDbModel(
        path_in_storage=path_in_storage,
        filename=filename,
        short_name=short_name,
        size=123,
        file_type='text/plain'
    )

    mock_pg_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=mock_file_record)
    mock_minio.get_presigned_url.return_value = mock_presigned_url
    response = await async_client.get(f'/presigned-url/{short_name}')
    assert response.status_code == 200
    assert response.json() == mock_presigned_url


@pytest.mark.anyio
async def test_get_presigned_url_not_found(mock_pg_session, async_client, refresh_clients_sessions):
    mock_pg_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)
    response = await async_client.get(f'/presigned-url/{short_name}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'File not found'}


@pytest.mark.anyio
async def test_save_file(file_service, mock_file):
    file_record = await file_service.save(mock_file, path)
    assert file_record.filename == mock_file.filename
    assert file_record.file_type == mock_file.content_type
    assert file_record.size == len(b"test content")
    assert file_record.path_in_storage == path
    file_service.db_session.add.assert_called_once()
    file_service.db_session.commit.assert_called_once()
    file_service.db_session.refresh.assert_called_once()


@pytest.mark.anyio
async def test_get_file_record_success(file_service, mock_pg_session):
    mock_file_record = FileDbModel(
        path_in_storage='test/path',
        filename=filename,
        short_name=short_name,
        size=123,
        file_type='text/plain',
    )
    mock_pg_session.execute.return_value.scalar_one_or_none = MagicMock(return_value=mock_file_record)
    file_record = await file_service.get_file_record(short_name)
    assert file_record == mock_file_record
