from fastapi import HTTPException


class NoSuchTokenUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Токен содержит данные о несуществующем пользователе!",
        )


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Необходимо передать Bearer-токен в заголовок Authorization!",
        )


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Истек срок действия токена!")


class JWTParseErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Произошла ошибка при считывании JWT-токена!",
        )


class RestrictedPermissionException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail=f"У Вас недостаточно прав для выполнения этого действия!",
        )


class InvalidTokenRevision(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail=f"Рефреш-токен потерял актуальность в виду изменений в пользователе! Необходимо залогиниться заново",
        )


class NotARefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail=f"Переданный токен не является Refresh!",
        )
