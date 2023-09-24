# -*- coding: utf-8 -*-

from argparse import Namespace
from copy import deepcopy
from typing import List, Optional

from uvicorn.config import LoopSetupType

from osom_api.arguments import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    PRINTER_ATTR_KEY,
)
from osom_api.logging.logging import logger


class Config:
    def __init__(
        self,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        timeout=DEFAULT_TIMEOUT,
        use_uvloop=False,
        debug=False,
        verbose=0,
        *,
        printer=print,
        args: Optional[Namespace] = None,
    ):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._use_uvloop = use_uvloop
        self._debug = debug
        self._verbose = verbose
        self._printer = printer
        self._args = deepcopy(args) if args is not None else Namespace()

    @classmethod
    def from_namespace(cls, args: Namespace):
        assert isinstance(args.host, str)
        assert isinstance(args.port, int)
        assert isinstance(args.timeout, float)
        assert isinstance(args.use_uvloop, bool)
        assert isinstance(args.debug, bool)
        assert isinstance(args.verbose, int)

        host = args.host
        port = args.port
        timeout = args.timeout
        use_uvloop = args.use_uvloop
        debug = args.debug
        verbose = args.verbose
        printer = getattr(args, PRINTER_ATTR_KEY, print)

        return cls(
            host=host,
            port=port,
            timeout=timeout,
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
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def timeout(self) -> float:
        return self._timeout

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
            f"Web host: '{self._host}'",
            f"Web port: {self._port}",
            f"Web timeout: {self._timeout:.3f}s",
            f"Use uvloop: {self._use_uvloop}",
            f"Debug: {self._debug}",
            f"Verbose: {self._verbose}",
        ]

    def logging_params(self) -> None:
        for line in self.as_logging_lines():
            logger.info(line)
