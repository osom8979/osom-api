# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import List, Optional

from type_serialize.inspect.member import get_public_instance_attributes
from uvicorn.config import LoopSetupType

from osom_api.arguments import (
    DEFAULT_HTTP_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_HTTP_TIMEOUT,
    DEFAULT_REDIS_CLOSE_TIMEOUT,
    DEFAULT_REDIS_CONNECTION_TIMEOUT,
    DEFAULT_REDIS_DATABASE,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
    DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
    DEFAULT_SEVERITY,
)
from osom_api.logging.logging import logger


class Config:
    def __init__(
        self,
        http_host=DEFAULT_HTTP_HOST,
        http_port=DEFAULT_HTTP_PORT,
        http_timeout=DEFAULT_HTTP_TIMEOUT,
        redis_host=DEFAULT_REDIS_HOST,
        redis_port=DEFAULT_REDIS_PORT,
        redis_database=DEFAULT_REDIS_DATABASE,
        redis_password: Optional[str] = None,
        redis_use_tls=False,
        redis_ca_cert: Optional[str] = None,
        redis_cert: Optional[str] = None,
        redis_key: Optional[str] = None,
        redis_connection_timeout=DEFAULT_REDIS_CONNECTION_TIMEOUT,
        redis_subscribe_timeout=DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
        redis_close_timeout=DEFAULT_REDIS_CLOSE_TIMEOUT,
        s3_endpoint: Optional[str] = None,
        s3_access: Optional[str] = None,
        s3_secret: Optional[str] = None,
        s3_region: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        severity=DEFAULT_SEVERITY,
        use_uvloop=False,
        debug=False,
        verbose=0,
        printer=print,
        **kwargs,
    ):
        self.http_host = http_host
        self.http_port = http_port
        self.http_timeout = http_timeout
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_database = redis_database
        self.redis_password = redis_password
        self.redis_use_tls = redis_use_tls
        self.redis_ca_cert = redis_ca_cert
        self.redis_cert = redis_cert
        self.redis_key = redis_key
        self.redis_connection_timeout = redis_connection_timeout
        self.redis_subscribe_timeout = redis_subscribe_timeout
        self.redis_close_timeout = redis_close_timeout
        self.s3_endpoint = s3_endpoint
        self.s3_access = s3_access
        self.s3_secret = s3_secret
        self.s3_region = s3_region
        self.s3_bucket = s3_bucket
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.severity = severity
        self.use_uvloop = use_uvloop
        self.debug = debug
        self.verbose = verbose
        self.printer = printer
        self.kwargs = kwargs

    @classmethod
    def from_namespace(cls, args: Namespace):
        assert isinstance(args.http_host, str)
        assert isinstance(args.http_port, int)
        assert isinstance(args.http_timeout, float)
        assert isinstance(args.severity, str)
        assert isinstance(args.use_uvloop, bool)
        assert isinstance(args.debug, bool)
        assert isinstance(args.verbose, int)
        return cls(**{k: v for k, v in get_public_instance_attributes(args)})

    @property
    def loop_setup_type(self) -> LoopSetupType:
        if self.use_uvloop:
            return "uvloop"
        else:
            return "asyncio"

    def print(self, *args, **kwargs):
        return self.printer(*args, **kwargs)

    def as_logging_lines(self) -> List[str]:
        return [
            f"HTTP host: '{self.http_host}'",
            f"HTTP port: {self.http_port}",
            f"HTTP timeout: {self.http_timeout:.3f}s",
            f"Use uvloop: {self.use_uvloop}",
            f"Debug: {self.debug}",
            f"Verbose: {self.verbose}",
        ]

    def logging_params(self) -> None:
        for line in self.as_logging_lines():
            logger.info(line)
