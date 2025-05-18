from app.ports.storage import IStoragePort
from app.config.app import Settings
from botocore.client import Config
import logging
import boto3
import io

LOGGER = logging.getLogger(__name__)


class S3StorageAdapter(IStoragePort):
    def __init__(self):
        self.__client = boto3.client(
            "s3",
            endpoint_url=Settings.S3_ENDPOINT,
            aws_access_key_id=Settings.S3_ACCESS_KEY,
            aws_secret_access_key=Settings.S3_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

        LOGGER.debug("Successfully connected to S3 client")

    def upload_jpeg(self, buf: io.BytesIO, bucket: str, key: str) -> None:
        try:
            self.__client.upload_fileobj(
                buf,
                bucket,
                key,
                ExtraArgs={"ContentType": "image/jpeg"},
            )
            LOGGER.info(f"Uploading JPEG with key {key}")
        except Exception as e:
            LOGGER.error(
                f"Error while uploading JPEG with key {key}", exc_info=True
            )
            raise

    def upload_file(
        self, buf: io.BytesIO, bucket: str, key: str, content_type: str
    ) -> None:
        try:
            self.__client.upload_fileobj(
                buf,
                bucket,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            LOGGER.info(f"Uploading file with key {key}")
        except Exception as e:
            LOGGER.error(
                f"Error while uploading file with key {key}", exc_info=True
            )
            raise

    def delete_object(self, bucket: str, key: str) -> None:
        try:
            self.__client.delete_object(Bucket=bucket, Key=key)
            LOGGER.info(f"Deleting object with key {key}")
        except Exception as e:
            LOGGER.error(f"Error while deleting object with key {key}")
            raise

    def object_exists(self, bucket: str, key: str) -> bool:
        try:
            self.__client.head_object(Bucket=bucket, Key=key)
            return True
        except self.__client.exceptions.ClientError:
            return False

    def get_object(self, bucket: str, key: str) -> dict:
        try:
            obj = self.__client.get_object(Bucket=bucket, Key=key)
            LOGGER.info(f"Getting object with key {key}")
            return obj
        except Exception as e:
            LOGGER.error(f"Error while getting object with key {key}")
            raise

    def ensure_bucket(self, bucket: str) -> None:
        if self.__client.bucket_exists(bucket):
            return

        raise RuntimeError(f"Необходимо определить бакет {bucket}!")
