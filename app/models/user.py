from tortoise.models import Model
from tortoise import fields
import bcrypt


class UserModel(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(null=False, max_length=60, unique=True)
    password_hash = fields.CharField(max_length=128)
    role = fields.CharField(max_length=16, default="user")

    first_name = fields.CharField(max_length=30)
    last_name = fields.CharField(max_length=30)
    patronymic = fields.CharField(max_length=30)

    def verify_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    class Meta:
        table: str = "users"
