from contextlib import asynccontextmanager
from miniopy_async import Minio
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from file_api.src.api.v1 import files
from file_api.src.core.config import minio_settings, app_settings
from file_api.src.db.minio import set_minio, create_bucket_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    minio_client = Minio(
        endpoint=f'{minio_settings.minio_host}:{minio_settings.minio_port}',
        access_key=minio_settings.minio_root_user,
        secret_key=minio_settings.minio_root_password,
        secure=False,
    )
    set_minio(minio_client)
    await create_bucket_if_not_exists(minio_settings.backet_name)

    yield


app = FastAPI(
    title=app_settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(files.router, prefix='/api/v1/files', tags=['files'])

