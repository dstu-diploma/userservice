from app.ports.storage import IStoragePort
import io


class MockS3Storage(IStoragePort):
    def __init__(self):
        self.uploaded_files = {}
        self.deleted_objects = set()
        self.existing_objects = set()
        self.objects_content = {}

    def upload_jpeg(self, buf: io.BytesIO, bucket: str, key: str) -> None:
        self.upload_file(buf, bucket, key, "image/jpeg")

    def upload_file(
        self, buf: io.BytesIO, bucket: str, key: str, content_type: str
    ) -> None:
        self.uploaded_files[(bucket, key)] = {
            "content": buf.getvalue(),
            "content_type": content_type,
        }
        self.existing_objects.add((bucket, key))
        self.objects_content[(bucket, key)] = {
            "Body": io.BytesIO(buf.getvalue()),
            "ContentType": content_type,
        }

    def delete_object(self, bucket: str, key: str) -> None:
        self.deleted_objects.add((bucket, key))
        self.existing_objects.discard((bucket, key))
        self.uploaded_files.pop((bucket, key), None)
        self.objects_content.pop((bucket, key), None)

    def object_exists(self, bucket: str, key: str) -> bool:
        return (bucket, key) in self.existing_objects

    def get_object(self, bucket: str, key: str) -> dict:
        if (bucket, key) not in self.existing_objects:
            raise FileNotFoundError(f"Object {bucket}/{key} not found")
        return self.objects_content[(bucket, key)]

    def ensure_bucket(self, bucket: str) -> None:
        return
