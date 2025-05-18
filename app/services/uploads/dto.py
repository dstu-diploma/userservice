from datetime import datetime
from pydantic import BaseModel

from app.models.user import UserUploadsModel, UserUploadsType


class UserUploadDto(BaseModel):
    user_id: int
    type: UserUploadsType
    s3_key: str
    content_type: str
    uploaded_at: datetime
    url: str | None

    @staticmethod
    def from_tortoise(upload: UserUploadsModel, url: str | None = None):
        return UserUploadDto(
            user_id=upload.user_id,  # type: ignore[attr-defined]
            type=upload.type,
            s3_key=upload.s3_key,
            content_type=upload.content_type,
            uploaded_at=upload.uploaded_at,
            url=url,
        )
