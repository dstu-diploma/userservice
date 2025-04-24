from fastapi import HTTPException


class WrongMimeException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Данный MIME-тип запрещен!")


class WrongMagicsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Формат файла запрещен!")


class ImageReadException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="Произошла ошибка при попытке считать изображение!",
        )


class ImageSaveException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="Произошла ошибка при попытке сохранить изображение!",
        )


class AvatarRemoveException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="Произошла ошибка при попытке удалить аватарку!",
        )


class NoAvatarException(HTTPException):
    def __init__(self):
        super().__init__(status_code=500, detail="Аватарки не существует!")
