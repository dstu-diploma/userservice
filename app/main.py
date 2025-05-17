from fastapi.middleware.cors import CORSMiddleware
from app.routers import main_router
from app.config import Settings
from fastapi import FastAPI
from app.db import init_db

app = FastAPI(
    title="DSTU Diploma | UserService",
    docs_url="/swagger",
    root_path=Settings.ROOT_PATH,
)
init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
