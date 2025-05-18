from app.acl.roles import UserRoles
from tortoise.models import Model
from tortoise import fields
from enum import StrEnum
import bcrypt


class UserModel(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(null=False, max_length=60, unique=True)
    password_hash = fields.CharField(max_length=128)
    role = fields.CharEnumField(
        enum_type=UserRoles, max_length=16, default=UserRoles.User
    )
    register_date = fields.DatetimeField(auto_now_add=True)

    first_name = fields.CharField(max_length=30)
    last_name = fields.CharField(max_length=30)
    patronymic = fields.CharField(max_length=30)

    about = fields.CharField(null=True, max_length=256)
    birthday = fields.DatetimeField(null=True)

    is_banned = fields.BooleanField(default=False)

    def verify_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    class Meta:
        table: str = "users"


class UserTokensModel(Model):
    id = fields.IntField(pk=True)
    token_revision = fields.IntField(default=0)
    user: fields.OneToOneRelation = fields.OneToOneField(
        "models.UserModel",
        related_name="users",
        on_delete=fields.CASCADE,
    )

    def verify_revision(self, rev: int):
        return self.token_revision == rev

    async def increase_revision(self):
        self.token_revision += 1
        await self.save(update_fields=("token_revision",))

    class Meta:
        table: str = "usertokens"


class UserUploadsType(StrEnum):
    Avatar = "avatar"
    Cover = "cover"


class UserUploadsModel(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        model_name="models.UserModel",
        related_name="uploads",
        on_delete=fields.CASCADE,
    )
    type = fields.CharEnumField(enum_type=UserUploadsType, max_length=16)
    s3_key = fields.CharField(max_length=256)
    content_type = fields.CharField(max_length=255)
    uploaded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "uploads"
        unique_together = (("user", "type"),)
