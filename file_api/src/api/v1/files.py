from http import HTTPStatus
from fastapi import APIRouter, UploadFile, HTTPException, Depends
from starlette.responses import StreamingResponse
from file_api.src.models.file import FileResponse
from file_api.src.services.files import FileService, get_file_service
from file_api.src.utils.exceptions import NotFoundException
import logging
router = APIRouter()


@router.post("/upload/", response_model=FileResponse)
async def upload_file(file: UploadFile,
                      path: str,
                      service: FileService = Depends(get_file_service)):
    try:
        file_record = await service.save(file, path)
        data= FileResponse(
            id=file_record.id,
            path_in_storage=file_record.path_in_storage,
            filename=file_record.filename,
            size=file_record.size,
            file_type=file_record.file_type,
            short_name=file_record.short_name,
            created_at=file_record.created_at,
            user_id=file_record.user_id
        )
        return data.model_dump()
    except Exception as e:
        logging.error(f"Ошибка при добавлении файла {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/download/{short_name}", response_class=StreamingResponse)
async def download_file(short_name: str, service: FileService = Depends(get_file_service)):
    try:
        file_record = await service.get_file_record(short_name)
        return await service.get_file(file_record.path_in_storage, file_record.filename)
    except NotFoundException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/presigned-url/{short_name}")
async def get_presigned_url(short_name: str, service: FileService = Depends(get_file_service)):
    try:
        file_record = await service.get_file_record(short_name)
        data = await service.get_presigned_url(file_record.path_in_storage)
        return data
    except NotFoundException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))