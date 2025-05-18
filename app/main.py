from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import get_event_publisher
from contextlib import asynccontextmanager
from app.routers import main_router
from app.config import Settings
from fastapi import FastAPI
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    publisher = get_event_publisher()
    await publisher.connect()

    yield


app = FastAPI(
    title="DSTU Diploma | UserService",
    docs_url="/swagger",
    root_path=Settings.ROOT_PATH,
    lifespan=lifespan,
)

init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
