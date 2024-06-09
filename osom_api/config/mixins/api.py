# -*- coding: utf-8 -*-

from typing import Optional


class ApiProps:
    api_http_host: str
    api_http_port: str
    api_http_timeout: float
    api_token: Optional[str]
    api_disable_auth: bool
    api_disable_docs: bool
    api_openapi_url: Optional[str]

    def assert_api_properties(self) -> None:
        assert isinstance(self.api_http_host, str)
        assert isinstance(self.api_http_port, int)
        assert isinstance(self.api_http_timeout, float)
        assert isinstance(self.api_token, (type(None), str))
        assert isinstance(self.api_disable_auth, bool)
        assert isinstance(self.api_disable_docs, bool)
        assert isinstance(self.api_openapi_url, (type(None), str))
