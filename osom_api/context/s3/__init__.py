# -*- coding: utf-8 -*-

from typing import BinaryIO, Optional

from boto3 import resource


class S3Client:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        access: Optional[str] = None,
        secret: Optional[str] = None,
        region: Optional[str] = None,
        bucket: Optional[str] = None,
    ):
        if all((endpoint, access, secret, region, bucket)):
            self._s3 = resource(
                service_name="s3",
                endpoint_url=endpoint,
                aws_access_key_id=access,
                aws_secret_access_key=secret,
                region_name=region,
            )
            self._bucket = self._s3.Bucket(bucket)
        else:
            self._s3 = None
            self._bucket = None

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        self._s3 = None

    @property
    def objects(self):
        return [obj for obj in self._bucket.objects.all()]

    @property
    def keys(self):
        return [obj.key for obj in self.objects]

    def exists_file(self, key: str) -> bool:
        try:
            self._bucket.Object(key).load()
        except:  # noqa
            return False
        else:
            return True

    def upload_file(self, file: str, key: str):
        return self._bucket.Object(key).upload_file(file)

    def download_file(self, key: str, file: str):
        return self._bucket.Object(key).download_file(file)

    def upload_data(self, data: BinaryIO, key: str):
        return self._bucket.Object(key).upload_fileobj(data)

    def download_data(self, key: str, data: BinaryIO):
        return self._bucket.Object(key).download_fileobj(data)
