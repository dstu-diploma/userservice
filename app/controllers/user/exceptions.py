from fastapi import HTTPException


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403, detail="Invalid or missing Bearer token!"
        )
