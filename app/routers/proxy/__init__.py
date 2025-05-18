from app.dependencies import get_storage_adapter, get_upload_service
from app.services.uploads.interface import IUserUploadService
from fastapi.responses import StreamingResponse
from app.ports.storage import IStoragePort
from fastapi import APIRouter, Depends
from urllib.parse import quote


router = APIRouter(prefix="/download", include_in_schema=False)


@router.get("/uploads/{s3_key}")
async def download_team_submission(
    s3_key: str,
    upload_service: IUserUploadService = Depends(get_upload_service),
    storage: IStoragePort = Depends(get_storage_adapter),
):
    upload = await upload_service.get_upload_by_key(s3_key)
    s3_obj = storage.get_object("avatars", upload.s3_key)

    return StreamingResponse(
        s3_obj["Body"],
        media_type=s3_obj["ContentType"],
        headers={
            "Content-Disposition": f'attachment; filename="{quote(f"{upload.type}_{upload.user_id}.jpg")}"'
        },
    )
