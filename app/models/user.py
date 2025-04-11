from tortoise.models import Model
from tortoise import fields
import bcrypt


class UserModel(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(null=False, max_length=60, unique=True)
    password_hash = fields.CharField(max_length=128)

    first_name = fields.CharField(max_length=30)
    last_name = fields.CharField(max_length=30)
    patronymic = fields.CharField(max_length=30)

    def verify_password(self, password):
        return bcrypt.checkpw(password, self.password_hash)

    class Meta:
        table: str = "users"
