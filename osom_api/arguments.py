# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from functools import lru_cache
from os import R_OK, access, getcwd
from os.path import isfile, join
from typing import Final, List, Optional

from osom_api.logging.logging import (
    DEFAULT_TIMED_ROTATING_WHEN,
    SEVERITIES,
    SEVERITY_NAME_INFO,
    TIMED_ROTATING_WHEN,
)
from osom_api.system.environ import get_typed_environ_value as get_eval

PROG: Final[str] = "osom-api"
DESCRIPTION: Final[str] = "API management toolkit for OSOM project"
EPILOG = f"""
Apply general debugging options:
  {PROG} -vv -c -d ...
"""

DEFAULT_SEVERITY: Final[str] = SEVERITY_NAME_INFO

CMD_DISCORD: Final[str] = "discord"
CMD_DISCORD_HELP: Final[str] = "Proxy server for Discord bots"
CMD_DISCORD_EPILOG: Final[str] = ""

CMD_TELEGRAM: Final[str] = "telegram"
CMD_TELEGRAM_HELP: Final[str] = "Proxy server for Telegram bots"
CMD_TELEGRAM_EPILOG: Final[str] = ""

CMD_MASTER: Final[str] = "master"
CMD_MASTER_HELP: Final[str] = "Endpoint server for HTTP API"
CMD_MASTER_EPILOG: Final[str] = ""

CMD_WORKER: Final[str] = "worker"
CMD_WORKER_HELP: Final[str] = "Worker nodes connected to message queue"
CMD_WORKER_EPILOG: Final[str] = ""

CMDS = (CMD_DISCORD, CMD_TELEGRAM, CMD_MASTER, CMD_WORKER)

DEFAULT_DOTENV_FILENAME: Final[str] = ".env.local"

DEFAULT_HTTP_HOST: Final[str] = "0.0.0.0"
DEFAULT_HTTP_PORT: Final[int] = 10503
DEFAULT_HTTP_TIMEOUT: Final[float] = 8.0

DEFAULT_API_OPENAPI_URL: Final[str] = "/spec/openapi.json"

_SECONDS_PER_HOUR: Final[int] = 60 * 60

DEFAULT_REDIS_CONNECTION_TIMEOUT: Final[float] = 16.0
DEFAULT_REDIS_SUBSCRIBE_TIMEOUT: Final[float] = 1.0 * _SECONDS_PER_HOUR
DEFAULT_REDIS_BLOCKING_TIMEOUT: Final[float] = 1.0 * _SECONDS_PER_HOUR
DEFAULT_REDIS_CLOSE_TIMEOUT: Final[float] = 4.0
DEFAULT_REDIS_EXPIRE_SHORT: Final[float] = 4.0
DEFAULT_REDIS_EXPIRE_MEDIUM: Final[float] = 8.0
DEFAULT_REDIS_EXPIRE_LONG: Final[float] = 12.0

DEFAULT_SUPABASE_POSTGREST_TIMEOUT: Final[float] = 8.0
DEFAULT_SUPABASE_STORAGE_TIMEOUT: Final[float] = 24.0

DEFAULT_OPENAI_TIMEOUT: Final[float] = 60.0

PRINTER_ATTR_KEY: Final[str] = "_printer"

VERBOSE_LEVEL_0: Final[int] = 0
VERBOSE_LEVEL_1: Final[int] = 1
VERBOSE_LEVEL_2: Final[int] = 2


@lru_cache
def version() -> str:
    # [IMPORTANT] Avoid 'circular import' issues
    from osom_api import __version__

    return __version__


def add_dotenv_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--no-dotenv",
        action="store_true",
        default=get_eval("NO_DOTENV", False),
        help="Do not use dot-env file",
    )
    parser.add_argument(
        "--dotenv-path",
        default=get_eval("DOTENV_PATH", join(getcwd(), DEFAULT_DOTENV_FILENAME)),
        metavar="file",
        help=f"Specifies the dot-env file (default: '{DEFAULT_DOTENV_FILENAME}')",
    )


def add_http_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--http-host",
        default=get_eval("HTTP_HOST", DEFAULT_HTTP_HOST),
        metavar="host",
        help=f"Host address (default: '{DEFAULT_HTTP_HOST}')",
    )
    parser.add_argument(
        "--http-port",
        default=get_eval("HTTP_PORT", DEFAULT_HTTP_PORT),
        metavar="port",
        type=int,
        help=f"Port number (default: {DEFAULT_HTTP_PORT})",
    )
    parser.add_argument(
        "--http-timeout",
        default=get_eval("HTTP_TIMEOUT", DEFAULT_HTTP_TIMEOUT),
        metavar="sec",
        type=float,
        help=f"Common timeout in seconds (default: {DEFAULT_HTTP_TIMEOUT})",
    )


def add_api_arguments(parser: ArgumentParser) -> None:
    api_token = get_eval("API_TOKEN", get_eval("OSOM_API_KEY", ""))
    parser.add_argument(
        "--api-token",
        default=api_token,
        metavar="token",
        help="API authentication token. if not specified, a random value is assigned.",
    )
    parser.add_argument(
        "--api-disable-auth",
        action="store_true",
        default=get_eval("API_DISABLE_AUTH", False),
        help="Disable authentication",
    )
    parser.add_argument(
        "--api-disable-docs",
        action="store_true",
        default=get_eval("API_DISABLE_DOCS", False),
        help="Disable documentation",
    )
    parser.add_argument(
        "--api-openapi-url",
        default=get_eval("API_OPENAPI_URL", DEFAULT_API_OPENAPI_URL),
        metavar="url",
        help=f"OpenAPI spec path (default: '{DEFAULT_API_OPENAPI_URL}')",
    )


def add_redis_arguments(
    parser: ArgumentParser,
    connection_timeout=DEFAULT_REDIS_CONNECTION_TIMEOUT,
    subscribe_timeout=DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
    blocking_timeout=DEFAULT_REDIS_BLOCKING_TIMEOUT,
    expire_short=DEFAULT_REDIS_EXPIRE_SHORT,
    expire_medium=DEFAULT_REDIS_EXPIRE_MEDIUM,
    expire_long=DEFAULT_REDIS_EXPIRE_LONG,
    close_timeout=DEFAULT_REDIS_CLOSE_TIMEOUT,
) -> None:
    parser.add_argument(
        "--redis-url",
        default=get_eval("REDIS_URL"),
        metavar="url",
        help="Redis URL",
    )

    parser.add_argument(
        "--redis-connection-timeout",
        default=get_eval("REDIS_CONNECTION_TIMEOUT", connection_timeout),
        metavar="sec",
        type=float,
        help=f"Redis connection timeout in seconds (default: {connection_timeout:.2f})",
    )
    parser.add_argument(
        "--redis-subscribe-timeout",
        default=get_eval("REDIS_SUBSCRIBE_TIMEOUT", subscribe_timeout),
        metavar="sec",
        type=float,
        help=f"Redis subscribe timeout in seconds (default: {subscribe_timeout:.2f})",
    )
    parser.add_argument(
        "--redis-blocking-timeout",
        default=get_eval("REDIS_BLOCKING_TIMEOUT", blocking_timeout),
        metavar="sec",
        type=float,
        help=f"Redis blocking timeout in seconds (default: {blocking_timeout:.2f})",
    )
    parser.add_argument(
        "--redis-close-timeout",
        default=get_eval("REDIS_CLOSE_TIMEOUT", close_timeout),
        metavar="sec",
        type=float,
        help=f"Redis close timeout in seconds (default: {close_timeout:.2f})",
    )

    parser.add_argument(
        "--redis-expire-short",
        default=get_eval("REDIS_EXPIRE_SHORT", expire_short),
        metavar="sec",
        type=float,
        help=f"Redis short expire seconds (default: {expire_short:.2f})",
    )
    parser.add_argument(
        "--redis-expire-medium",
        default=get_eval("REDIS_EXPIRE_MEDIUM", expire_medium),
        metavar="sec",
        type=float,
        help=f"Redis medium expire seconds (default: {expire_medium:.2f})",
    )
    parser.add_argument(
        "--redis-expire-long",
        default=get_eval("REDIS_EXPIRE_LONG", expire_long),
        metavar="sec",
        type=float,
        help=f"Redis long expire seconds (default: {expire_long:.2f})",
    )


def add_s3_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--s3-endpoint",
        default=get_eval("S3_ENDPOINT"),
        metavar="url",
        help="S3 Endpoint URL",
    )
    parser.add_argument(
        "--s3-access",
        default=get_eval("S3_ACCESS"),
        metavar="key",
        help="S3 Access Key ID",
    )
    parser.add_argument(
        "--s3-secret",
        default=get_eval("S3_SECRET"),
        metavar="key",
        help="S3 Secret Access Key",
    )
    parser.add_argument(
        "--s3-region",
        default=get_eval("S3_REGION"),
        metavar="region",
        help="S3 Region Name",
    )
    parser.add_argument(
        "--s3-bucket",
        default=get_eval("S3_BUCKET"),
        metavar="bucket",
        help="S3 Bucket Name",
    )


def add_supabase_arguments(
    parser: ArgumentParser,
    postgrest_timeout=DEFAULT_SUPABASE_POSTGREST_TIMEOUT,
    storage_timeout=DEFAULT_SUPABASE_STORAGE_TIMEOUT,
) -> None:
    supabase_url = get_eval("SUPABASE_URL", get_eval("NEXT_PUBLIC_SUPABASE_URL", ""))
    supabase_key = get_eval("SUPABASE_KEY", get_eval("SUPABASE_SERVICE_ROLE_KEY", ""))

    parser.add_argument(
        "--supabase-url",
        default=supabase_url if supabase_url else None,
        metavar="url",
        help="Supabase project URL",
    )
    parser.add_argument(
        "--supabase-key",
        default=supabase_key if supabase_key else None,
        metavar="key",
        help="Supabase service_role Key",
    )

    parser.add_argument(
        "--supabase-postgrest-timeout",
        default=get_eval("SUPABASE_POSTGREST_TIMEOUT", postgrest_timeout),
        metavar="sec",
        type=float,
        help=f"SyncPostgrestClient timeout. (default: {postgrest_timeout:.2f})",
    )
    parser.add_argument(
        "--supabase-storage-timeout",
        default=get_eval("SUPABASE_STORAGE_TIMEOUT", storage_timeout),
        metavar="sec",
        type=float,
        help=f"SyncStorageClient timeout. (default: {storage_timeout:.2f})",
    )


def add_openai_arguments(
    parser: ArgumentParser,
    openai_timeout=DEFAULT_OPENAI_TIMEOUT,
) -> None:
    parser.add_argument(
        "--openai-api-key",
        default=get_eval("OPENAI_API_KEY"),
        metavar="key",
        help="OpenAI API Key",
    )
    parser.add_argument(
        "--openai-timeout",
        default=get_eval("OPENAI_TIMEOUT", openai_timeout),
        metavar="sec",
        type=float,
        help=f"OpenAI timeout. (default: {openai_timeout:.2f})",
    )


def add_telegram_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--telegram-token",
        default=get_eval("TELEGRAM_TOKEN"),
        metavar="token",
        help="Telegram API Token",
    )


def add_discord_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--discord-application-id",
        default=get_eval("DISCORD_APPLICATION_ID"),
        metavar="id",
        help="Discord Application ID",
    )
    parser.add_argument(
        "--discord-token",
        default=get_eval("DISCORD_TOKEN"),
        metavar="token",
        help="Discord API Token",
    )


def _add_context_arguments(parser: ArgumentParser) -> None:
    add_redis_arguments(parser)
    add_s3_arguments(parser)
    add_supabase_arguments(parser)
    add_openai_arguments(parser)


def add_cmd_discord_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_DISCORD,
        help=CMD_DISCORD_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_DISCORD_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    _add_context_arguments(parser)
    add_discord_arguments(parser)


def add_cmd_telegram_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_TELEGRAM,
        help=CMD_TELEGRAM_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_TELEGRAM_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    _add_context_arguments(parser)
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
    _add_context_arguments(parser)
    add_http_arguments(parser)
    add_api_arguments(parser)


def add_cmd_worker_parser(subparsers) -> None:
    # [IMPORTANT] Avoid 'circular import' issues
    from osom_api.context.mq.path import QUEUE_COMMON_PATH

    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_WORKER,
        help=CMD_WORKER_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_WORKER_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    _add_context_arguments(parser)
    parser.add_argument(
        "--request-key",
        default=get_eval("REQUEST_KEY", QUEUE_COMMON_PATH),
        metavar="key",
        help=f"Request key path (default: '{QUEUE_COMMON_PATH}')",
    )


def default_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )

    add_dotenv_arguments(parser)

    logging_group = parser.add_mutually_exclusive_group()
    logging_group.add_argument(
        "--colored-logging",
        "-c",
        action="store_true",
        default=get_eval("COLORED_LOGGING", False),
        help="Use colored logging",
    )
    logging_group.add_argument(
        "--default-logging",
        action="store_true",
        default=get_eval("DEFAULT_LOGGING", False),
        help="Use default logging",
    )
    logging_group.add_argument(
        "--simple-logging",
        "-s",
        action="store_true",
        default=get_eval("SIMPLE_LOGGING", False),
        help="Use simple logging",
    )

    parser.add_argument(
        "--rotate-logging-prefix",
        default=get_eval("ROTATE_LOGGING_PREFIX", ""),
        metavar="prefix",
        help="Rotate logging prefix",
    )
    parser.add_argument(
        "--rotate-logging-when",
        choices=TIMED_ROTATING_WHEN,
        default=get_eval("ROTATE_LOGGING_WHEN", DEFAULT_TIMED_ROTATING_WHEN),
        help=f"Rotate logging when (default: '{DEFAULT_TIMED_ROTATING_WHEN}')",
    )

    parser.add_argument(
        "--use-uvloop",
        action="store_true",
        default=get_eval("USE_UVLOOP", False),
        help="Replace the event loop with uvloop",
    )
    parser.add_argument(
        "--severity",
        choices=SEVERITIES,
        default=get_eval("SEVERITY", DEFAULT_SEVERITY),
        help=f"Logging severity (default: '{DEFAULT_SEVERITY}')",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=get_eval("DEBUG", False),
        help="Enable debugging mode and change logging severity to 'DEBUG'",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=get_eval("VERBOSE", 0),
        help="Be more verbose/talkative during the operation",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=version(),
    )

    subparsers = parser.add_subparsers(dest="cmd")
    add_cmd_discord_parser(subparsers)
    add_cmd_telegram_parser(subparsers)
    add_cmd_master_parser(subparsers)
    add_cmd_worker_parser(subparsers)
    return parser


def _load_dotenv(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> None:
    parser = ArgumentParser(add_help=False, allow_abbrev=False, exit_on_error=False)
    add_dotenv_arguments(parser)
    args = parser.parse_known_args(cmdline, namespace)[0]

    assert isinstance(args.no_dotenv, bool)
    assert isinstance(args.dotenv_path, str)

    if args.no_dotenv:
        return
    if not isfile(args.dotenv_path):
        return
    if not access(args.dotenv_path, R_OK):
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(args.dotenv_path)
    except ModuleNotFoundError:
        pass


def _remove_dotenv_attrs(namespace: Namespace) -> Namespace:
    assert isinstance(namespace.no_dotenv, bool)
    assert isinstance(namespace.dotenv_path, str)

    del namespace.no_dotenv
    del namespace.dotenv_path

    assert not hasattr(namespace, "no_dotenv")
    assert not hasattr(namespace, "dotenv_path")

    return namespace


def get_default_arguments(
    cmdline: Optional[List[str]] = None,
    namespace: Optional[Namespace] = None,
) -> Namespace:
    # [IMPORTANT] Dotenv related options are processed first.
    _load_dotenv(cmdline, namespace)

    parser = default_argument_parser()
    args = parser.parse_known_args(cmdline, namespace)[0]

    # Remove unnecessary dotenv attrs
    return _remove_dotenv_attrs(args)
