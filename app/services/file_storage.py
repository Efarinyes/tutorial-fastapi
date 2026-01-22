import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException, status


MEDIA_DIR = 'app/media'
ALLOW_MIME = ['image/jpeg', 'image/jpg', 'image/png']

def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)

def save_upload_file(file: UploadFile) -> dict:
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail='Invalid file type. Only jpg, jpeg, or png are allowed.')

    ensure_media_dir()
    ext = os.path.splitext(file.filename)[1]
    filename = f'{uuid.uuid4().hex}{ext}'
    file_path = os.path.join(MEDIA_DIR, filename)
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    return {
        'filename': filename,
        'content_type': file.content_type,
        'url': f'/media/{filename}'
    }
