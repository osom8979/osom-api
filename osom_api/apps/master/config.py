# -*- coding: utf-8 -*-

from argparse import Namespace
from copy import deepcopy
from typing import List, Optional

from uvicorn.config import LoopSetupType

from osom_api.arguments import (
    DEFAULT_HTTP_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_HTTP_TIMEOUT,
    PRINTER_ATTR_KEY,
)
from osom_api.logging.logging import logger


class Config:
    def __init__(
        self,
        http_host=DEFAULT_HTTP_HOST,
        http_port=DEFAULT_HTTP_PORT,
        http_timeout=DEFAULT_HTTP_TIMEOUT,
        use_uvloop=False,
        debug=False,
        verbose=0,
        *,
        printer=print,
        args: Optional[Namespace] = None,
    ):
        self._http_host = http_host
        self._http_port = http_port
        self._http_timeout = http_timeout
        self._use_uvloop = use_uvloop
        self._debug = debug
        self._verbose = verbose
        self._printer = printer
        self._args = deepcopy(args) if args is not None else Namespace()

    @classmethod
    def from_namespace(cls, args: Namespace):
        assert isinstance(args.http_host, str)
        assert isinstance(args.http_port, int)
        assert isinstance(args.http_timeout, float)
        assert isinstance(args.use_uvloop, bool)
        assert isinstance(args.debug, bool)
        assert isinstance(args.verbose, int)

        http_host = args.http_host
        http_port = args.http_port
        http_timeout = args.http_timeout
        use_uvloop = args.use_uvloop
        debug = args.debug
        verbose = args.verbose
        printer = getattr(args, PRINTER_ATTR_KEY, print)

        return cls(
            http_host=http_host,
            http_port=http_port,
            http_timeout=http_timeout,
            use_uvloop=use_uvloop,
            debug=debug,
            verbose=verbose,
            printer=printer,
            args=args,
        )

    @property
    def args(self) -> Namespace:
        return self._args

    @property
    def http_host(self) -> str:
        return self._http_host

    @property
    def http_port(self) -> int:
        return self._http_port

    @property
    def http_timeout(self) -> float:
        return self._http_timeout

    @property
    def use_uvloop(self) -> bool:
        return self._use_uvloop

    @property
    def loop_setup_type(self) -> LoopSetupType:
        if self._use_uvloop:
            return "uvloop"
        else:
            return "asyncio"

    @property
    def debug(self) -> bool:
        return self._debug

    @property
    def verbose(self) -> int:
        return self._verbose

    def print(self, *args, **kwargs):
        return self._printer(*args, **kwargs)

    def as_logging_lines(self) -> List[str]:
        return [
            f"HTTP host: '{self._http_host}'",
            f"HTTP port: {self._http_port}",
            f"HTTP timeout: {self._http_timeout:.3f}s",
            f"Use uvloop: {self._use_uvloop}",
            f"Debug: {self._debug}",
            f"Verbose: {self._verbose}",
        ]

    def logging_params(self) -> None:
        for line in self.as_logging_lines():
            logger.info(line)
