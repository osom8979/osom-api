# -*- coding: utf-8 -*-

from typing import Optional

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
        if all((endpoint, access, secret, region)):
            self._s3 = resource(
                service_name="s3",
                endpoint_url=endpoint,
                aws_access_key_id=access,
                aws_secret_access_key=secret,
                region_name=region,
            )
        else:
            self._s3 = None
        self._bucket = bucket

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        self._s3 = None
