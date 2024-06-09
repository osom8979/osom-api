# -*- coding: utf-8 -*-

from asyncio import to_thread
from typing import Any, BinaryIO, Dict, Optional

from boto3 import client as boto3_client
from botocore.exceptions import ClientError

from osom_api.args.redis import RedisArgs
from osom_api.context.s3.protocol.client import ALLOWED_UPLOAD_ARGS, Client
from osom_api.exceptions import AlreadyInitializedError, NotInitializedError
from osom_api.logging.logging import logger


class S3Client:
    _client: Optional[Client]

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access: Optional[str] = None,
        secret: Optional[str] = None,
        region: Optional[str] = None,
        bucket: Optional[str] = None,
    ):
        self._endpoint = endpoint
        self._access = access
        self._secret = secret
        self._region = region
        self._bucket = bucket if bucket else str()
        self._client = None

    @classmethod
    def from_args(cls, args: RedisArgs):
        return cls(
            endpoint=args.s3_endpoint,
            access=args.s3_access,
            secret=args.s3_secret,
            region=args.s3_region,
            bucket=args.s3_bucket,
        )

    async def open(self) -> None:
        if self._client is not None:
            raise AlreadyInitializedError("S3 client already initialized")

        # [IMPORTANT] bucket name is also required.
        values = self._endpoint, self._access, self._secret, self._region, self._bucket
        if not all(values):
            logger.warning("S3 client is not initialized")
            return

        assert isinstance(self._endpoint, str)
        assert isinstance(self._access, str)
        assert isinstance(self._secret, str)
        assert isinstance(self._region, str)
        assert self._region in ("wnam", "enam", "weur", "eeur", "apac", "auto")

        self._client = boto3_client(
            service_name="s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=self._access,
            aws_secret_access_key=self._secret,
            region_name=self._region,
        )
        logger.info("S3 client initialized")

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None
        logger.debug("S3 client closed")

    @property
    def client(self) -> Client:
        if self._client is None:
            raise NotInitializedError("Client is not initialized")
        return self._client

    def synced_list_objects(self):
        result = self.client.list_objects(Bucket=self._bucket)
        assert isinstance(result, dict)
        assert isinstance(result["ResponseMetadata"], dict)
        assert isinstance(result["IsTruncated"], bool)
        assert isinstance(result["Marker"], str)
        assert isinstance(result["Name"], str) and result["Name"] == self._bucket
        assert isinstance(result["Prefix"], str)
        assert isinstance(result["MaxKeys"], int)
        return result

    def synced_head_object(self, key: str):
        return self.client.head_object(Bucket=self._bucket, Key=key)

    def synced_has_object(self, key: str):
        try:
            self.synced_head_object(key)
        except ClientError:
            return False
        else:
            return True

    def synced_delete_object(self, key: str):
        return self.client.delete_object(Bucket=self._bucket, Key=key)

    def synced_get_object(self, key: str):
        return self.client.get_object(Bucket=self._bucket, Key=key)

    def synced_upload_file(
        self,
        file: str,
        key: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if extra is not None:
            for k in extra.keys():
                assert k in ALLOWED_UPLOAD_ARGS
        self.client.upload_file(
            Filename=file,
            Bucket=self._bucket,
            Key=key,
            ExtraArgs=extra,
        )

    def synced_upload_data(
        self,
        data: BinaryIO,
        key: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if extra is not None:
            for k in extra.keys():
                assert k in ALLOWED_UPLOAD_ARGS
        self.client.upload_fileobj(
            Fileobj=data,
            Bucket=self._bucket,
            Key=key,
            ExtraArgs=extra,
        )

    def synced_download_file(self, key: str, file: str) -> None:
        self.client.download_file(Bucket=self._bucket, Key=key, Filename=file)

    def synced_download_data(self, key: str, data: BinaryIO) -> None:
        self.client.download_fileobj(Bucket=self._bucket, Key=key, Fileobj=data)

    def synced_generate_presigned_url(
        self,
        client_method: str,
        params: Dict[str, Any],
        expires=3600.0,
        http_method: Optional[str] = None,
    ):
        return self.client.generate_presigned_url(
            ClientMethod=client_method,
            Params=params,
            ExpiresIn=int(expires),
            HttpMethod=http_method,
        )

    async def list_objects(self) -> Dict[str, Any]:
        return await to_thread(self.synced_list_objects)

    async def head_object(self, key: str) -> Dict[str, Any]:
        return await to_thread(self.synced_head_object, key)

    async def has_object(self, key: str) -> bool:
        try:
            await to_thread(self.synced_head_object, key)
        except ClientError:
            return False
        else:
            return True

    async def delete_object(self, key: str) -> Dict[str, Any]:
        return await to_thread(self.synced_delete_object, key)

    async def get_object(self, key: str) -> Dict[str, Any]:
        return await to_thread(self.synced_get_object, key)

    async def upload_file(
        self,
        file: str,
        key: str,
        content_type: Optional[str] = None,
    ) -> None:
        extra = dict()
        if content_type:
            extra["ContentType"] = content_type
        await to_thread(self.synced_upload_file, file, key, extra)

    async def upload_data(
        self,
        data: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
    ) -> None:
        extra = dict()
        if content_type:
            extra["ContentType"] = content_type
        await to_thread(self.synced_upload_data, data, key, extra)

    async def download_file(self, key: str, file: str) -> None:
        await to_thread(self.synced_download_file, key, file)

    async def download_data(self, key: str, data: BinaryIO) -> None:
        await to_thread(self.synced_download_data, key, data)

    async def generate_presigned_url(
        self,
        client_method: str,
        params: Dict[str, Any],
        expires=3600.0,
        http_method: Optional[str] = None,
    ) -> str:
        return await to_thread(
            self.synced_generate_presigned_url,
            client_method,
            params,
            expires,
            http_method,
        )
