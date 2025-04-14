from pydantic import BaseModel, StringConstraints
from typing import Annotated


class PasswordDto(BaseModel):
    password: Annotated[str, StringConstraints(min_length=8)]
