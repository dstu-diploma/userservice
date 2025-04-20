from fastapi import HTTPException


class NoSuchUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="No user with such UserID!")


class UserWithThatEmailExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="User with such email already exists!"
        )


class InvalidLoginCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Invalid email or password!")
