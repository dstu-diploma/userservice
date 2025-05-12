from app.ports.istorageport import IStoragePort
from botocore.client import Config
from os import environ
import boto3
import io


S3_AUTOCREATE_BUCKETS = environ.get("S3_AUTOCREATE_BUCKETS", "False") == "True"


class S3Adapter(IStoragePort):
    def __init__(self):
        self.__client = boto3.client(
            "s3",
            endpoint_url=environ.get("S3_ENDPOINT"),
            aws_access_key_id=environ.get("S3_ACCESS_KEY"),
            aws_secret_access_key=environ.get("S3_SECRET_KEY"),
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def upload_jpeg(self, buf: io.BytesIO, bucket: str, key: str) -> None:
        self.__client.upload_fileobj(
            buf,
            bucket,
            key,
            ExtraArgs={"ContentType": "image/jpeg"},
        )

    def delete_object(self, bucket: str, key: str) -> None:
        self.__client.delete_object(Bucket=bucket, Key=key)

    def object_exists(self, bucket: str, key: str) -> bool:
        try:
            self.__client.head_object(Bucket=bucket, Key=key)
            return True
        except self.__client.exceptions.ClientError:
            return False

    def ensure_bucket(self, bucket: str) -> None:
        if self.__client.bucket_exists(bucket):
            return

        if S3_AUTOCREATE_BUCKETS:
            self.__client.make_bucket(bucket)
        else:
            raise RuntimeError(f"Необходимо определить бакет {bucket}!")
