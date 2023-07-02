# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from functools import lru_cache
from typing import Final, List, Optional

from osom_work.logging.logging import SEVERITIES, SEVERITY_NAME_INFO

CMD_MASTER: Final[str] = "master"
CMD_WORKER: Final[str] = "worker"

PROG: Final[str] = "osom-work"
DESCRIPTION: Final[str] = "osom master and worker"
EPILOG: Final[str] = ""

DEFAULT_SEVERITY: Final[str] = SEVERITY_NAME_INFO

CMDS = (CMD_MASTER, CMD_WORKER)

CMD_MASTER_HELP: Final[str] = "Master node"
CMD_MASTER_EPILOG: Final[str] = ""

CMD_WORKER_HELP: Final[str] = "Worker node"
CMD_WORKER_EPILOG: Final[str] = ""

DEFAULT_BIND: Final[str] = "0.0.0.0"
DEFAULT_PORT: Final[int] = 8080
DEFAULT_TIMEOUT: Final[float] = 8.0
DEFAULT_BROKER: Final[str] = ""


@lru_cache
def version() -> str:
    # [IMPORTANT] Avoid 'circular import' issues
    from osom_work import __version__

    return __version__


def add_cmd_master_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_MASTER,
        help=CMD_MASTER_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_MASTER_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)

    parser.add_argument(
        "--bind",
        "-b",
        default=DEFAULT_BIND,
        metavar="bind",
        help=f"Bind address (default: '{DEFAULT_BIND}')",
    )
    parser.add_argument(
        "--port",
        "-p",
        default=DEFAULT_PORT,
        metavar="port",
        type=int,
        help=f"Port number (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        default=DEFAULT_TIMEOUT,
        metavar="sec",
        type=float,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--broker",
        "-B",
        default=DEFAULT_BROKER,
        metavar="bind",
        type=str,
        help=f"URL of the default broker used (default: '{DEFAULT_BROKER}')",
    )


def add_cmd_worker_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_WORKER,
        help=CMD_WORKER_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_WORKER_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)

    parser.add_argument(
        "--timeout",
        "-t",
        default=DEFAULT_TIMEOUT,
        type=float,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "broker",
        help="URL of the default broker used",
    )


def default_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--colored-logging",
        "-c",
        action="store_true",
        default=False,
        help="Use colored logging",
    )
    parser.add_argument(
        "--simple-logging",
        "-s",
        action="store_true",
        default=False,
        help="Use simple logging",
    )
    parser.add_argument(
        "--severity",
        choices=SEVERITIES,
        default=DEFAULT_SEVERITY,
        help=f"Logging severity (default: '{DEFAULT_SEVERITY}')",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=False,
        help="Enable debugging mode and change logging severity to 'DEBUG'",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Be more verbose/talkative during the operation",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=version(),
    )

    subparsers = parser.add_subparsers(dest="cmd")
    add_cmd_master_parser(subparsers)
    add_cmd_worker_parser(subparsers)
    return parser


def get_default_arguments(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> Namespace:
    parser = default_argument_parser()
    return parser.parse_known_args(cmdline, namespace)[0]
