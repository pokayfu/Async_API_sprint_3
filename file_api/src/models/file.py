from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional

class FileResponse(BaseModel):
    id: UUID4
    path_in_storage: str
    filename: str
    size: int
    file_type: str
    short_name: str
    created_at: datetime
    user_id: UUID4 | None
