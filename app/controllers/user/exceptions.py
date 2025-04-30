from fastapi import HTTPException


class NoSuchUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404, detail="Пользователя с данным ID не существует!"
        )


class NoUserWithSuchEmailException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404, detail="Пользователя с данным Email не существует!"
        )


class UserWithThatEmailExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="На данную почту уже зарегистрирован пользователь!!",
        )


class InvalidLoginCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Неверный логин или пароль!")
