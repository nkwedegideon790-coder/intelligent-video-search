from fastapi import APIRouter, UploadFile
import os


router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_file(file: UploadFile):
    save_Dir = "uploaded_files"
    # creats the directory if it does not exist
    if not os.path.exists(save_Dir):
        os.makedirs(save_Dir)
    file_path = os.path.join(save_Dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())