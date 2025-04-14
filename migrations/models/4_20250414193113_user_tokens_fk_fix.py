from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usertokens" DROP CONSTRAINT IF EXISTS "fk_usertoke_users_bf0466a7";
        ALTER TABLE "usertokens" ADD CONSTRAINT "fk_usertoke_users_bf0466a7" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_usertokens_user_id_05e74d" ON "usertokens" ("user_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_usertokens_user_id_05e74d";
        ALTER TABLE "usertokens" DROP CONSTRAINT IF EXISTS "fk_usertoke_users_bf0466a7";
        ALTER TABLE "usertokens" ADD CONSTRAINT "fk_usertoke_users_bf0466a7" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""
