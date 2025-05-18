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


class FileRemoveException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="Произошла ошибка при попытке удалить файл!",
        )


class NoFileException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Файла не существует!")


class TooSmallImageException(HTTPException):
    def __init__(self, w: int, h: int, min_w: int, min_h: int):
        super().__init__(
            status_code=400,
            detail=f"Размер изображения слишком мал! Минимум: {min_w}x{min_h}. У Вас: {w}x{h}!",
        )


class TooBigImageException(HTTPException):
    def __init__(self, w: int, h: int, max_w: int, max_h: int):
        super().__init__(
            status_code=400,
            detail=f"Размер изображения слишком большой! Максимум: {max_w}x{max_h}. У Вас: {w}x{h}!",
        )
