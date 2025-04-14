from fastapi import APIRouter
from .root import router as root_router

main_router = APIRouter(tags=["Основные"])
main_router.include_router(root_router)
