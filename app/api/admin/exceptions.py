from fastapi import HTTPException


class CantChangeSelfRoleException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Вы не можете менять роль самому себе!"
        )


class CantDeleteSelfException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Вы не можете удалить самого себя!"
        )


class CantBanSelfException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Вы не можете заблокировать самого себя!"
        )
