# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Any, Dict, List, Optional, Union

from type_serialize.inspect.member import get_public_instance_attributes

from osom_api.arguments import (
    DEFAULT_CHAT_MODEL,
    DEFAULT_OPENAI_TIMEOUT,
    DEFAULT_REDIS_BLOCKING_TIMEOUT,
    DEFAULT_REDIS_CLOSE_TIMEOUT,
    DEFAULT_REDIS_CONNECTION_TIMEOUT,
    DEFAULT_REDIS_EXPIRE_LONG,
    DEFAULT_REDIS_EXPIRE_MEDIUM,
    DEFAULT_REDIS_EXPIRE_SHORT,
    DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
    DEFAULT_SEVERITY,
    DEFAULT_SUPABASE_POSTGREST_TIMEOUT,
    DEFAULT_SUPABASE_STORAGE_TIMEOUT,
)
from osom_api.commands import COMMAND_PREFIX
from osom_api.logging.logging import DEBUG, convert_level_number, logger


class Config:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_connection_timeout=DEFAULT_REDIS_CONNECTION_TIMEOUT,
        redis_subscribe_timeout=DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
        redis_blocking_timeout=DEFAULT_REDIS_BLOCKING_TIMEOUT,
        redis_close_timeout=DEFAULT_REDIS_CLOSE_TIMEOUT,
        redis_expire_short=DEFAULT_REDIS_EXPIRE_SHORT,
        redis_expire_medium=DEFAULT_REDIS_EXPIRE_MEDIUM,
        redis_expire_long=DEFAULT_REDIS_EXPIRE_LONG,
        s3_endpoint: Optional[str] = None,
        s3_access: Optional[str] = None,
        s3_secret: Optional[str] = None,
        s3_region: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        supabase_postgrest_timeout=DEFAULT_SUPABASE_POSTGREST_TIMEOUT,
        supabase_storage_timeout=DEFAULT_SUPABASE_STORAGE_TIMEOUT,
        openai_api_key: Optional[str] = None,
        openai_timeout=DEFAULT_OPENAI_TIMEOUT,
        openai_default_chat_model=DEFAULT_CHAT_MODEL,
        command_prefix=COMMAND_PREFIX,
        severity=DEFAULT_SEVERITY,
        use_uvloop=False,
        debug=False,
        verbose=0,
        printer=print,
        **kwargs,
    ):
        self.redis_url = redis_url
        self.redis_connection_timeout = redis_connection_timeout
        self.redis_subscribe_timeout = redis_subscribe_timeout
        self.redis_blocking_timeout = redis_blocking_timeout
        self.redis_close_timeout = redis_close_timeout
        self.redis_expire_short = redis_expire_short
        self.redis_expire_medium = redis_expire_medium
        self.redis_expire_long = redis_expire_long
        self.s3_endpoint = s3_endpoint
        self.s3_access = s3_access
        self.s3_secret = s3_secret
        self.s3_region = s3_region
        self.s3_bucket = s3_bucket
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_postgrest_timeout = supabase_postgrest_timeout
        self.supabase_storage_timeout = supabase_storage_timeout
        self.openai_api_key = openai_api_key
        self.openai_timeout = openai_timeout
        self.openai_default_chat_model = openai_default_chat_model
        self.command_prefix = command_prefix
        self.severity = severity
        self.use_uvloop = use_uvloop
        self.debug = debug
        self.verbose = verbose
        self.printer = printer
        self.kwargs = kwargs

    @classmethod
    def from_namespace(cls, args: Namespace):
        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))

    @staticmethod
    def assert_common_properties(args: Namespace) -> None:
        assert isinstance(args.redis_url, (type(None), str))
        assert isinstance(args.redis_connection_timeout, float)
        assert isinstance(args.redis_subscribe_timeout, float)
        assert isinstance(args.redis_blocking_timeout, float)
        assert isinstance(args.redis_close_timeout, float)
        assert isinstance(args.redis_expire_short, float)
        assert isinstance(args.redis_expire_medium, float)
        assert isinstance(args.redis_expire_long, float)

        assert isinstance(args.s3_endpoint, (type(None), str))
        assert isinstance(args.s3_access, (type(None), str))
        assert isinstance(args.s3_secret, (type(None), str))
        assert isinstance(args.s3_region, (type(None), str))
        assert isinstance(args.s3_bucket, (type(None), str))

        assert isinstance(args.supabase_url, (type(None), str))
        assert isinstance(args.supabase_key, (type(None), str))
        assert isinstance(args.supabase_postgrest_timeout, float)
        assert isinstance(args.supabase_storage_timeout, float)

        assert isinstance(args.openai_api_key, (type(None), str))
        assert isinstance(args.openai_timeout, float)
        assert isinstance(args.openai_default_chat_model, str)

        assert isinstance(args.command_prefix, str)

        assert isinstance(args.severity, str)
        assert isinstance(args.use_uvloop, bool)
        assert isinstance(args.debug, bool)
        assert isinstance(args.verbose, int)

    @staticmethod
    def namespace_to_dict(args: Namespace) -> Dict[str, Any]:
        return {k: v for k, v in get_public_instance_attributes(args)}

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
