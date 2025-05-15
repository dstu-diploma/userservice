from pydantic import BaseModel


class AccessTokenDto(BaseModel):
    access_token: str
