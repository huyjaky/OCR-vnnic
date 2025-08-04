from pydantic import BaseModel
from fastapi import UploadFile, File

class FileType(BaseModel):
    file: UploadFile = File(...)
    is_remove: bool = True # Default to True, indicating the file should be removed after processing
