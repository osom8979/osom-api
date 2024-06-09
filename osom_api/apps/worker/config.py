# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.config.base import BaseConfig
from osom_api.config.mixins import (
    CommonProps,
    ModuleProps,
    RedisProps,
    S3Props,
    SupabaseProps,
)


class WorkerConfig(
    BaseConfig,
    CommonProps,
    RedisProps,
    S3Props,
    SupabaseProps,
    ModuleProps,
):
    def __init__(self, args: Namespace):
        super().__init__(**self.namespace_to_dict(args))
        self.assert_common_properties()
        self.assert_redis_properties()
        self.assert_s3_properties()
        self.assert_supabase_properties()
        self.assert_module_properties()
