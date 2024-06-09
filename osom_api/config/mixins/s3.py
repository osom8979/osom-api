# -*- coding: utf-8 -*-

from typing import Optional


class S3Props:
    s3_endpoint: Optional[str] = None
    s3_access: Optional[str] = None
    s3_secret: Optional[str] = None
    s3_region: Optional[str] = None
    s3_bucket: Optional[str] = None

    def assert_s3_properties(self) -> None:
        assert isinstance(self.s3_endpoint, (type(None), str))
        assert isinstance(self.s3_access, (type(None), str))
        assert isinstance(self.s3_secret, (type(None), str))
        assert isinstance(self.s3_region, (type(None), str))
        assert isinstance(self.s3_bucket, (type(None), str))
