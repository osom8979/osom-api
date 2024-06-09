# -*- coding: utf-8 -*-

from typing import Optional

from osom_api.args._common import CommonArgs


class RedisArgs(CommonArgs):
    redis_url: Optional[str]
    redis_connection_timeout: Optional[float]
    redis_subscribe_timeout: Optional[float]
    redis_blocking_timeout: float
    redis_close_timeout: float
    redis_expire_short: float
    redis_expire_medium: float
    redis_expire_long: float
    redis_ssl_cert_reqs: str

    def assert_redis_properties(self) -> None:
        assert isinstance(self.redis_url, (type(None), str))
        assert isinstance(self.redis_connection_timeout, (type(None), float))
        assert isinstance(self.redis_subscribe_timeout, (type(None), float))
        assert isinstance(self.redis_blocking_timeout, float)
        assert isinstance(self.redis_close_timeout, float)
        assert isinstance(self.redis_expire_short, float)
        assert isinstance(self.redis_expire_medium, float)
        assert isinstance(self.redis_expire_long, float)
        assert isinstance(self.redis_ssl_cert_reqs, str)
