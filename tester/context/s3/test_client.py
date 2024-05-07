# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Tuple
from unittest import IsolatedAsyncioTestCase, main, skipIf

from dotenv import dotenv_values

from osom_api.assets import get_osom_logo_svg_path
from osom_api.context.s3 import S3Client
from tester import get_root_dotenv_local_path


def get_dotenv_s3_values() -> Optional[Tuple[str, str, str, str, str]]:
    values = dotenv_values(get_root_dotenv_local_path())
    endpoint = values.get("S3_ENDPOINT")
    access = values.get("S3_ACCESS")
    secret = values.get("S3_SECRET")
    region = values.get("S3_REGION")
    bucket = values.get("S3_BUCKET")
    if all((endpoint, access, secret, region, bucket)):
        assert isinstance(endpoint, str)
        assert isinstance(access, str)
        assert isinstance(secret, str)
        assert isinstance(region, str)
        assert isinstance(bucket, str)
        return endpoint, access, secret, region, bucket
    else:
        return None


@skipIf(get_dotenv_s3_values() is None, "An environment variable for S3 is not defined")
class S3ClientTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        values = get_dotenv_s3_values()
        self.assertIsNotNone(values)
        endpoint, access, secret, region, bucket = values
        self.s3 = S3Client(endpoint, access, secret, region, bucket)

    async def asyncSetUp(self):
        await self.s3.open()

    async def asyncTearDown(self):
        await self.s3.close()

    async def test_upload_and_download(self):
        key = "/tester/logo.svg"
        src = get_osom_logo_svg_path()
        try:
            self.assertFalse(await self.s3.has_object(key))

            await self.s3.upload_file(str(src), key)
            self.assertTrue(await self.s3.has_object(key))

            with TemporaryDirectory() as tmpdir:
                dest = Path(tmpdir) / "logo.svg"
                self.assertFalse(dest.exists())

                await self.s3.download_file(key, str(dest))
                self.assertTrue(dest.is_file())

                self.assertEqual(src.read_bytes(), dest.read_bytes())
        finally:
            if await self.s3.has_object(key):
                await self.s3.delete_object(key)
            self.assertFalse(await self.s3.has_object(key))


if __name__ == "__main__":
    main()
