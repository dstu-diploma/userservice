from . import auth_pb2_grpc, auth_pb2
from typing import Protocol
from os import environ
import grpc


class IAuthServiceClient(Protocol):
    async def init_user(self, user_id: int, role: str): ...
    async def generate_key_pair(self, user_id: int, role: str): ...
    async def generate_access_token(self, user_id: int, refresh_token: str): ...
    async def generate_refresh_token(self, user_id: int, role: str): ...
    async def validate_refresh_token(self, token: str): ...
    async def close(self): ...


class AuthServiceClient(IAuthServiceClient):
    def __init__(self, address: str = "localhost:50051"):
        self.channel = grpc.aio.insecure_channel(address)
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    async def init_user(self, user_id: int, role: str):
        req = auth_pb2.UserRequest(user_id=user_id, role=role)
        return await self.stub.InitUser(req)

    async def generate_key_pair(self, user_id: int, role: str):
        req = auth_pb2.UserRequest(user_id=user_id, role=role)
        return await self.stub.GenerateKeyPair(req)

    async def generate_access_token(self, user_id: int, refresh_token: str):
        req = auth_pb2.AccessTokenRequest(
            user_id=user_id, refresh_token=refresh_token
        )
        return await self.stub.GenerateAccessToken(req)

    async def generate_refresh_token(self, user_id: int, role: str):
        req = auth_pb2.UserRequest(user_id=user_id, role=role)
        return await self.stub.GenerateRefreshToken(req)

    async def validate_refresh_token(self, token: str):
        req = auth_pb2.TokenValidationRequest(token=token)
        return await self.stub.ValidateRefreshToken(req)

    async def close(self):
        await self.channel.close()


# TODO: без глобала? наверное

GRPC_AUTH_SERVICE_URL = environ.get("GRPC_AUTH_SERVICE_URL", "localhost:50051")
AUTH_CLIENT = AuthServiceClient(GRPC_AUTH_SERVICE_URL)


def get_auth_client() -> AuthServiceClient:
    return AUTH_CLIENT
