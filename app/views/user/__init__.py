from app.controllers import user as user_controller
from fastapi import APIRouter, Depends, Query
from app.grpc.auth import AuthServiceClient, get_auth_client


router = APIRouter(prefix="")


@router.post("/", response_model=user_controller.FullUserDto)
async def create(
    user_dto: user_controller.CreateUserDto,
    auth_service: AuthServiceClient = Depends(get_auth_client),
):
    user = await user_controller.create(user_dto.password, user_dto)
    await auth_service.init_user(user.id, "user")
    return user


@router.patch("/", response_model=user_controller.FullUserDto)
async def update(update_dto: user_controller.OptionalFullUserData):
    return await user_controller.update_info(update_dto)


@router.delete("/")
async def delete(user_id: int = Query(..., ge=0)):
    return await user_controller.delete(user_id)


@router.get("/")
async def get_all():
    return await user_controller.get_all()
