from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)



class FileAlreadyExists(HTTPException):
    def __init__(self):
        detail="File already exists"
        super().__init__(status_code=404, detail=detail)
