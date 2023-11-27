# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from functools import lru_cache
from os import getcwd, path
from typing import Final, List, Optional

from osom_api.logging.logging import (
    DEFAULT_TIMED_ROTATING_WHEN,
    SEVERITIES,
    SEVERITY_NAME_INFO,
    TIMED_ROTATING_WHEN,
)
from osom_api.system.environ import get_typed_environ_value as defval

PROG: Final[str] = "osom-api"
DESCRIPTION: Final[str] = "osom master and worker"
EPILOG: Final[str] = ""

DEFAULT_SEVERITY: Final[str] = SEVERITY_NAME_INFO

CMD_BOT: Final[str] = "bot"
CMD_BOT_HELP: Final[str] = "Bot"
CMD_BOT_EPILOG: Final[str] = ""

CMD_MASTER: Final[str] = "master"
CMD_MASTER_HELP: Final[str] = "Master node"
CMD_MASTER_EPILOG: Final[str] = ""

CMD_WORKER: Final[str] = "worker"
CMD_WORKER_HELP: Final[str] = "Worker node"
CMD_WORKER_EPILOG: Final[str] = ""

CMDS = (CMD_BOT, CMD_MASTER, CMD_WORKER)

DEFAULT_HTTP_HOST: Final[str] = "0.0.0.0"
DEFAULT_HTTP_PORT: Final[int] = 10503  # ap1.0503.run
DEFAULT_HTTP_TIMEOUT: Final[float] = 8.0

DEFAULT_REDIS_HOST: Final[str] = "localhost"
DEFAULT_REDIS_PORT: Final[int] = 6379
DEFAULT_REDIS_DATABASE: Final[int] = 0
DEFAULT_REDIS_CONNECTION_TIMEOUT: Final[float] = 8.0
DEFAULT_REDIS_SUBSCRIBE_TIMEOUT: Final[float] = 4.0
DEFAULT_REDIS_CLOSE_TIMEOUT: Final[float] = 12.0

PRINTER_ATTR_KEY: Final[str] = "_printer"

DOTENV_FILENAME: Final[str] = ".env"

VERBOSE_LEVEL_0: Final[int] = 0
VERBOSE_LEVEL_1: Final[int] = 1
VERBOSE_LEVEL_2: Final[int] = 2


@lru_cache
def version() -> str:
    # [IMPORTANT] Avoid 'circular import' issues
    from osom_api import __version__

    return __version__


def add_http_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--http-host",
        default=defval("HTTP_HOST", DEFAULT_HTTP_HOST),
        metavar="host",
        help=f"Host address (default: '{DEFAULT_HTTP_HOST}')",
    )
    parser.add_argument(
        "--http-port",
        default=defval("HTTP_PORT", DEFAULT_HTTP_PORT),
        metavar="port",
        type=int,
        help=f"Port number (default: {DEFAULT_HTTP_PORT})",
    )
    parser.add_argument(
        "--http-timeout",
        default=defval("HTTP_TIMEOUT", DEFAULT_HTTP_TIMEOUT),
        metavar="sec",
        type=float,
        help=f"Common timeout in seconds (default: {DEFAULT_HTTP_TIMEOUT})",
    )


def add_redis_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--redis-host",
        default=defval("REDIS_HOST", DEFAULT_REDIS_HOST),
        metavar="host",
        help=f"Redis host address (default: '{DEFAULT_REDIS_HOST}')",
    )
    parser.add_argument(
        "--redis-port",
        default=defval("REDIS_PORT", DEFAULT_REDIS_PORT),
        metavar="port",
        type=int,
        help=f"Redis port number (default: {DEFAULT_REDIS_PORT})",
    )
    parser.add_argument(
        "--redis-database",
        default=defval("REDIS_DATABASE", DEFAULT_REDIS_DATABASE),
        metavar="index",
        type=int,
        help=f"Redis database index (default: {DEFAULT_REDIS_DATABASE})",
    )
    parser.add_argument(
        "--redis-password",
        default=defval("REDIS_PASSWORD"),
        metavar="passwd",
        help="Redis password",
    )

    parser.add_argument(
        "--redis-use-tls",
        action="store_true",
        default=defval("REDIS_USE_TLS", False),
        help="Enable redis TLS mode",
    )
    parser.add_argument(
        "--redis-ca-cert",
        default=defval("REDIS_CA_CERT"),
        help="CA Certificate file to verify with",
    )
    parser.add_argument(
        "--redis-cert",
        default=defval("REDIS_CERT"),
        help="Client certificate to authenticate with",
    )
    parser.add_argument(
        "--redis-key",
        default=defval("REDIS_KEY"),
        help="Private key file to authenticate with",
    )

    redis_connection_timeout_help = (
        f"Redis connection timeout in seconds "
        f"(default: {DEFAULT_REDIS_CONNECTION_TIMEOUT:.2f})"
    )
    parser.add_argument(
        "--redis-connection-timeout",
        default=defval("REDIS_CONNECTION_TIMEOUT", DEFAULT_REDIS_CONNECTION_TIMEOUT),
        metavar="sec",
        type=float,
        help=redis_connection_timeout_help,
    )

    redis_subscribe_timeout_help = (
        f"Redis subscribe timeout in seconds "
        f"(default: {DEFAULT_REDIS_SUBSCRIBE_TIMEOUT:.2f})"
    )
    parser.add_argument(
        "--redis-subscribe-timeout",
        default=defval("REDIS_SUBSCRIBE_TIMEOUT", DEFAULT_REDIS_SUBSCRIBE_TIMEOUT),
        metavar="sec",
        type=float,
        help=redis_subscribe_timeout_help,
    )

    redis_close_timeout_help = (
        f"Redis close timeout in seconds "
        f"(default: {DEFAULT_REDIS_CLOSE_TIMEOUT:.2f})"
    )
    parser.add_argument(
        "--redis-close-timeout",
        default=defval("REDIS_CLOSE_TIMEOUT", DEFAULT_REDIS_CLOSE_TIMEOUT),
        metavar="sec",
        type=float,
        help=redis_close_timeout_help,
    )


def add_s3_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--s3-endpoint",
        default=defval("S3_ENDPOINT"),
        metavar="url",
        help="S3 Endpoint URL",
    )
    parser.add_argument(
        "--s3-access",
        default=defval("S3_ACCESS"),
        metavar="key",
        help="S3 Access Key ID",
    )
    parser.add_argument(
        "--s3-secret",
        default=defval("S3_SECRET"),
        metavar="key",
        help="S3 Secret Access Key",
    )
    parser.add_argument(
        "--s3-region",
        default=defval("S3_REGION"),
        metavar="region",
        help="S3 Region Name",
    )
    parser.add_argument(
        "--s3-bucket",
        default=defval("S3_BUCKET"),
        metavar="bucket",
        help="S3 Bucket Name",
    )


def add_supabase_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--supabase-url",
        default=defval("SUPABASE_URL"),
        metavar="url",
        help="Supabase Project URL",
    )
    parser.add_argument(
        "--supabase-key",
        default=defval("SUPABASE_KEY"),
        metavar="key",
        help="Supabase Anon Key",
    )


def add_telegram_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--telegram-token",
        default=defval("TELEGRAM_TOKEN"),
        metavar="token",
        help="Telegram API Token",
    )


def add_cmd_bot_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_BOT,
        help=CMD_BOT_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_BOT_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    add_redis_arguments(parser)
    add_s3_arguments(parser)
    add_supabase_arguments(parser)
    add_telegram_arguments(parser)


def add_cmd_master_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_MASTER,
        help=CMD_MASTER_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_MASTER_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    add_http_arguments(parser)
    add_redis_arguments(parser)
    add_s3_arguments(parser)
    add_supabase_arguments(parser)


def add_cmd_worker_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_WORKER,
        help=CMD_WORKER_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_WORKER_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    add_redis_arguments(parser)
    add_s3_arguments(parser)
    add_supabase_arguments(parser)


def default_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )

    logging_group = parser.add_mutually_exclusive_group()
    logging_group.add_argument(
        "--colored-logging",
        "-c",
        action="store_true",
        default=defval("COLORED_LOGGING", False),
        help="Use colored logging",
    )
    logging_group.add_argument(
        "--default-logging",
        action="store_true",
        default=defval("DEFAULT_LOGGING", False),
        help="Use default logging",
    )
    logging_group.add_argument(
        "--simple-logging",
        "-s",
        action="store_true",
        default=defval("SIMPLE_LOGGING", False),
        help="Use simple logging",
    )

    parser.add_argument(
        "--rotate-logging-prefix",
        default=defval("ROTATE_LOGGING_PREFIX", ""),
        help="Rotate logging prefix",
    )
    parser.add_argument(
        "--rotate-logging-when",
        choices=TIMED_ROTATING_WHEN,
        default=defval("ROTATE_LOGGING_WHEN", DEFAULT_TIMED_ROTATING_WHEN),
        help=f"Rotate logging when (default: '{DEFAULT_TIMED_ROTATING_WHEN}')",
    )

    parser.add_argument(
        "--use-uvloop",
        action="store_true",
        default=defval("USE_UVLOOP", False),
        help="Replace the event loop with uvloop",
    )
    parser.add_argument(
        "--severity",
        choices=SEVERITIES,
        default=defval("SEVERITY", DEFAULT_SEVERITY),
        help=f"Logging severity (default: '{DEFAULT_SEVERITY}')",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=defval("DEBUG", False),
        help="Enable debugging mode and change logging severity to 'DEBUG'",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=defval("VERBOSE", 0),
        help="Be more verbose/talkative during the operation",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=version(),
    )

    subparsers = parser.add_subparsers(dest="cmd")
    add_cmd_bot_parser(subparsers)
    add_cmd_master_parser(subparsers)
    add_cmd_worker_parser(subparsers)
    return parser


def _load_dotenv(dotenv_path: str) -> None:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path)


def get_default_arguments(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
    load_dotenv=False,
) -> Namespace:
    if load_dotenv:
        dotenv_path = path.join(getcwd(), DOTENV_FILENAME)
        if path.isfile(dotenv_path):
            _load_dotenv(dotenv_path)

    parser = default_argument_parser()
    return parser.parse_known_args(cmdline, namespace)[0]
