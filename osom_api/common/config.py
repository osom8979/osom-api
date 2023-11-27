# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Any, Dict, List, Optional, Union

from type_serialize.inspect.member import get_public_instance_attributes

from osom_api.arguments import (
    DEFAULT_REDIS_CLOSE_TIMEOUT,
    DEFAULT_REDIS_CONNECTION_TIMEOUT,
    DEFAULT_REDIS_DATABASE,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
    DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
    DEFAULT_SEVERITY,
)
from osom_api.logging.logging import DEBUG, convert_level_number, logger


class CommonConfig:
    def __init__(
        self,
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

    @staticmethod
    def assert_common_properties(args: Namespace) -> None:
        assert isinstance(args.redis_host, (type(None), str))
        assert isinstance(args.redis_port, int)
        assert isinstance(args.redis_database, int)
        assert isinstance(args.redis_password, (type(None), str))
        assert isinstance(args.redis_use_tls, bool)
        assert isinstance(args.redis_ca_cert, (type(None), str))
        assert isinstance(args.redis_cert, (type(None), str))
        assert isinstance(args.redis_key, (type(None), str))
        assert isinstance(args.redis_connection_timeout, float)
        assert isinstance(args.redis_subscribe_timeout, float)
        assert isinstance(args.redis_close_timeout, float)

        assert isinstance(args.s3_endpoint, (type(None), str))
        assert isinstance(args.s3_access, (type(None), str))
        assert isinstance(args.s3_secret, (type(None), str))
        assert isinstance(args.s3_region, (type(None), str))
        assert isinstance(args.s3_bucket, (type(None), str))

        assert isinstance(args.supabase_url, (type(None), str))
        assert isinstance(args.supabase_key, (type(None), str))

        assert isinstance(args.severity, str)
        assert isinstance(args.use_uvloop, bool)
        assert isinstance(args.debug, bool)
        assert isinstance(args.verbose, int)

    @staticmethod
    def namespace_to_dict(args: Namespace) -> Dict[str, Any]:
        return {k: v for k, v in get_public_instance_attributes(args)}

    @property
    def valid_supabase_params(self) -> bool:
        return all((self.supabase_url, self.supabase_key))

    @property
    def valid_s3_params(self) -> bool:
        return all(
            (
                self.s3_endpoint,
                self.s3_access,
                self.s3_secret,
                self.s3_region,
                self.s3_bucket,
            )
        )

    def print(self, *args, **kwargs):
        return self.printer(*args, **kwargs)

    def as_logging_lines(self) -> List[str]:
        result = list()
        for key, value in get_public_instance_attributes(self):
            name = key.replace("_", " ")
            name = name[0].upper() + name[1:]
            result.append(f"{name}: {value}")
        return result

    def logging_params(self, level: Union[str, int] = DEBUG) -> None:
        for line in self.as_logging_lines():
            logger.log(convert_level_number(level), line)
