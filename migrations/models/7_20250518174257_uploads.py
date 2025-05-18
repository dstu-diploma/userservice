from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "uploads" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(16) NOT NULL,
    "s3_key" VARCHAR(256) NOT NULL,
    "content_type" VARCHAR(255) NOT NULL,
    "uploaded_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_uploads_user_id_9b80f8" UNIQUE ("user_id", "type")
    );
    COMMENT ON COLUMN "uploads"."type" IS 'Avatar: avatar\nCover: cover';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "uploads";"""
