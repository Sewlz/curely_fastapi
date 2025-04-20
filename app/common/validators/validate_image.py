import imghdr
import os
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = {"jpeg", "png", "jpg"}

def validate_image_file(file: UploadFile):
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB allowed.")

    file.file.seek(0)
    file_type = imghdr.what(file.file)
    file.file.seek(0)
    if file_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")

    filename = os.path.basename(file.filename)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid or dangerous filename.")
