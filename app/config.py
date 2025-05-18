from pydantic_settings import BaseSettings, SettingsConfigDict


class UserServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DATABASE_URL: str

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    INTERNAL_API_KEY: str = "apikey"
    JWT_SECRET: str = "dstu"
    ROOT_PATH: str = ""
    PUBLIC_API_URL: str = "http://localhost/user/"


Settings = UserServiceSettings()
