from fastapi import HTTPException


class NoSuchTokenUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Token contains UserID for non-existant user!",
        )


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403, detail="Invalid or missing Bearer token!"
        )


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Token has expired!")


class JWTParseErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403, detail="An error occured during JWT parsing!"
        )


class RestrictedRolesException(HTTPException):
    def __init__(self, allowed_roles_str: str):
        super().__init__(
            status_code=403,
            detail=f"You dont have enough permissions. Allowed roles: {allowed_roles_str}",
        )


class InvalidTokenRevision(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail=f"Refresh token contains invalid revision number! Please login again!",
        )
