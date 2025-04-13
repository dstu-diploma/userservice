from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.user import (
    OptionalFullUserData,
    get_user_controller,
    UserController,
    CreateUserDto,
    FullUserDto,
    RegisteredUserDto,
)
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="")


@router.post("/", response_model=RegisteredUserDto)
async def create(
    user_dto: CreateUserDto,
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.create(user_dto.password, user_dto)


@router.post("/login", response_model=RegisteredUserDto)
async def login(
    input: OAuth2PasswordRequestForm = Depends(),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.login(input.username, input.password)


@router.patch("/", response_model=FullUserDto)
async def update(
    update_dto: OptionalFullUserData,
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.update_info(update_dto)


@router.delete("/")
async def delete(
    user_id: int = Query(..., ge=0),
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.delete(user_id)


@router.get("/")
async def get_all(
    user_controller: UserController = Depends(get_user_controller),
):
    return await user_controller.get_all()
