from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "birthday" TIMESTAMPTZ;
        ALTER TABLE "users" ADD "register_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "users" ADD "about" VARCHAR(256);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "birthday";
        ALTER TABLE "users" DROP COLUMN "register_date";
        ALTER TABLE "users" DROP COLUMN "about";"""
