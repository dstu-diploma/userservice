from pydantic import BaseModel


class SearchUserDto(BaseModel):
    id: int | None = None
    email: str | None = None
