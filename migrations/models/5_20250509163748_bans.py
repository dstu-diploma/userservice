from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "is_banned" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "users" ALTER COLUMN "role" TYPE VARCHAR(16) USING "role"::VARCHAR(16);
        COMMENT ON COLUMN "users"."role" IS 'User: user
Organizer: organizer
Helper: helper
Judge: judge
Admin: admin';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "is_banned";
        ALTER TABLE "users" ALTER COLUMN "role" TYPE VARCHAR(16) USING "role"::VARCHAR(16);
        COMMENT ON COLUMN "users"."role" IS NULL;"""
