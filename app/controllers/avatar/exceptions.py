from fastapi import HTTPException


class WrongMimeException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Wrong MIME type!")


class WrongMagicsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Wrong image type!")


class ImageReadException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500, detail="Error during opening the image!"
        )


class ImageSaveException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500, detail="Error during saving the image!"
        )


class AvatarRemoveException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500, detail="Error during deleting the avatar!"
        )


class NoAvatarException(HTTPException):
    def __init__(self):
        super().__init__(status_code=500, detail="Cant find the avatar!")
