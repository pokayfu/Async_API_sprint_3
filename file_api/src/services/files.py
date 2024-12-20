import logging
import urllib
from datetime import timedelta
from functools import lru_cache
from aiohttp import ClientSession
from fastapi import UploadFile, Depends
from miniopy_async import Minio
from miniopy_async.datatypes import Object as MinioObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import StreamingResponse
from file_api.src.core.config import  minio_settings
from file_api.src.db.pg import get_db_session
from file_api.src.db.minio import get_minio
from file_api.src.models.file_db import FileDbModel
from shortuuid import uuid as shortuuid
from file_api.src.utils.exceptions import NotFoundException, FileAlreadyExists
from file_api.src.core.config import app_settings


class FileService:
    def __init__(self, minio: Minio, db_session: AsyncSession) -> None:
        self.client = minio
        self.db_session = db_session

    async def save(self, file: UploadFile, path: str) -> FileDbModel:
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)
        await self.does_file_already_exists(minio_settings.backet_name, path)
        await self.client.put_object(
            bucket_name=minio_settings.backet_name, object_name=path,
            data=file.file, length=file_size,
            part_size=10 * 1024 * 1024,
        )
        new_file = FileDbModel(
            path_in_storage=path,
            filename=file.filename,
            short_name=shortuuid(),
            size=file_size,
            file_type=file.content_type,
        )

        self.db_session.add(new_file)
        await self.db_session.commit()
        await self.db_session.refresh(new_file)
        return new_file

    async def get_file_record(self, short_name: str) -> FileDbModel:
        file_record = await self.db_session.execute(
            select(FileDbModel).where(FileDbModel.short_name == short_name)
        )
        file_record = file_record.scalar_one_or_none()
        if not file_record:
            raise NotFoundException(detail='File not found')
        return file_record

    async def get_file(self, path: str, filename: str) -> StreamingResponse:
        async def file_stream():
            try:
                async with ClientSession() as session:
                    result = await self.client.get_object(minio_settings.backet_name, path, session=session)
                    async for chunk in result.content.iter_chunked(32 * 1024):
                        yield chunk
            except Exception as e:
                logging.error(f'Failed to download file: {e}')
                return
        return StreamingResponse(
            file_stream(),
            media_type='application/octet-stream',
            headers={"Content-Disposition": f'filename="{filename}"'}
        )

    async def get_presigned_url(self, path: str) -> str:
        return await self.client.get_presigned_url('GET', minio_settings.backet_name, path, expires=timedelta(days=1),
                                                   change_host=f'http://{app_settings.uvicorn_host}:{minio_settings.minio_port}')

    async def does_file_already_exists(self, bucket, path) -> bool:
        try:
            stat =  await self.client.stat_object(bucket, path)
        except Exception as e:
            return
        if stat and type(stat) is MinioObject:
            logging.error(f'Failed to upload the file, the filepath already exists - path: {path}')
            raise FileAlreadyExists


@lru_cache()
def get_file_service(minio: Minio = Depends(get_minio),
        db_session: AsyncSession = Depends(get_db_session)) -> FileService:
    return FileService(minio, db_session)