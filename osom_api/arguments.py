# -*- coding: utf-8 -*-

from argparse import REMAINDER, ArgumentParser, Namespace, RawDescriptionHelpFormatter
from functools import lru_cache
from os import R_OK, access, getcwd
from os.path import isfile, join
from typing import Final, List, Literal, Optional, Sequence, get_args

from osom_api.commands import COMMAND_PREFIX
from osom_api.logging.logging import (
    DEFAULT_TIMED_ROTATING_WHEN,
    SEVERITIES,
    SEVERITY_NAME_INFO,
    TIMED_ROTATING_WHEN,
)
from osom_api.random.hex import generate_hexdigits
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
CMD_DISCORD_EPILOG = f"""
Simply usage:
  {PROG} {CMD_DISCORD}
"""

CMD_TELEGRAM: Final[str] = "telegram"
CMD_TELEGRAM_HELP: Final[str] = "Proxy server for Telegram bots"
CMD_TELEGRAM_EPILOG = f"""
Simply usage:
  {PROG} {CMD_TELEGRAM}
"""

CMD_MASTER: Final[str] = "master"
CMD_MASTER_HELP: Final[str] = "Endpoint server for HTTP API"
CMD_MASTER_EPILOG = f"""
Simply usage:
  {PROG} {CMD_MASTER}
"""

CMD_WORKER: Final[str] = "worker"
CMD_WORKER_HELP: Final[str] = "Worker nodes connected to message queue"
CMD_WORKER_EPILOG = f"""
Simply usage:
  {PROG} {CMD_WORKER}
"""

CMDS = (CMD_DISCORD, CMD_TELEGRAM, CMD_MASTER, CMD_WORKER)

DEFAULT_DOTENV_FILENAME: Final[str] = ".env.local"
TEST_DOTENV_FILENAME: Final[str] = ".env.test"

DEFAULT_API_HTTP_HOST: Final[str] = "0.0.0.0"
DEFAULT_API_HTTP_PORT: Final[int] = 10503
DEFAULT_API_HTTP_TIMEOUT: Final[float] = 8.0
DEFAULT_API_OPENAPI_URL: Final[str] = "/spec/openapi.json"

RedisSslCertReqsLiteral = Literal["none", "optional", "required"]
REDIS_SSL_CERT_REQS: Final[Sequence[str]] = get_args(RedisSslCertReqsLiteral)
DEFAULT_REDIS_SSL_CERT_REQS: Final[str] = "none"

DEFAULT_REDIS_BLOCKING_TIMEOUT: Final[float] = 0.0
DEFAULT_REDIS_CLOSE_TIMEOUT: Final[float] = 4.0
DEFAULT_REDIS_EXPIRE_SHORT: Final[float] = 4.0
DEFAULT_REDIS_EXPIRE_MEDIUM: Final[float] = 8.0
DEFAULT_REDIS_EXPIRE_LONG: Final[float] = 12.0

DEFAULT_SUPABASE_POSTGREST_TIMEOUT: Final[float] = 8.0
DEFAULT_SUPABASE_STORAGE_TIMEOUT: Final[float] = 24.0

DEFAULT_MODULE_PATH: Final[str] = "osom_api.worker.modules.default"

OSOM_WEB_LINK: Final[str] = "https://www.osom.run/"
NOT_REGISTERED_MSG: Final[str] = f"Not registered. Go to {OSOM_WEB_LINK} and sign up!"

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


def add_api_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--api-http-bind",
        default=get_eval("API_HTTP_HOST", DEFAULT_API_HTTP_HOST),
        metavar="host",
        help=f"Host address (default: '{DEFAULT_API_HTTP_HOST}')",
    )
    parser.add_argument(
        "--api-http-port",
        default=get_eval("API_HTTP_PORT", DEFAULT_API_HTTP_PORT),
        metavar="port",
        type=int,
        help=f"Port number (default: {DEFAULT_API_HTTP_PORT})",
    )
    parser.add_argument(
        "--api-http-timeout",
        default=get_eval("API_HTTP_TIMEOUT", DEFAULT_API_HTTP_TIMEOUT),
        metavar="sec",
        type=float,
        help=f"Common timeout in seconds (default: {DEFAULT_API_HTTP_TIMEOUT})",
    )
    parser.add_argument(
        "--api-token",
        default=get_eval("API_TOKEN", generate_hexdigits(256)),
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


def add_module_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--module-path",
        "-m",
        default=get_eval("MODULE_PATH", DEFAULT_MODULE_PATH),
        metavar="path",
        help=f"Import path of the module to use (default: '{DEFAULT_MODULE_PATH}')",
    )
    parser.add_argument(
        "--module-isolate",
        action="store_true",
        default=get_eval("MODULE_ISOLATE", False),
        help="Enable isolated module",
    )
    parser.add_argument(
        "opts",
        nargs=REMAINDER,
        help="Arguments of module",
    )


def add_redis_arguments(
    parser: ArgumentParser,
    blocking_timeout=DEFAULT_REDIS_BLOCKING_TIMEOUT,
    expire_short=DEFAULT_REDIS_EXPIRE_SHORT,
    expire_medium=DEFAULT_REDIS_EXPIRE_MEDIUM,
    expire_long=DEFAULT_REDIS_EXPIRE_LONG,
    close_timeout=DEFAULT_REDIS_CLOSE_TIMEOUT,
    ssl_cert_reqs=DEFAULT_REDIS_SSL_CERT_REQS,
) -> None:
    parser.add_argument(
        "--redis-url",
        default=get_eval("REDIS_URL"),
        metavar="url",
        help="Redis URL",
    )

    parser.add_argument(
        "--redis-connection-timeout",
        default=get_eval("REDIS_CONNECTION_TIMEOUT"),
        metavar="sec",
        type=float,
        help="Redis connection timeout in seconds",
    )
    parser.add_argument(
        "--redis-subscribe-timeout",
        default=get_eval("REDIS_SUBSCRIBE_TIMEOUT"),
        metavar="sec",
        type=float,
        help="Redis subscribe timeout in seconds",
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

    parser.add_argument(
        "--redis-ssl-cert-reqs",
        choices=REDIS_SSL_CERT_REQS,
        default=get_eval("REDIS_SSL_CERT_REQS", ssl_cert_reqs),
        help=f"Verify mode of SSL Context (default: '{ssl_cert_reqs}')",
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


def _add_base_context_arguments(parser: ArgumentParser) -> None:
    add_redis_arguments(parser)
    add_s3_arguments(parser)
    add_supabase_arguments(parser)


def add_discord_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_DISCORD,
        help=CMD_DISCORD_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_DISCORD_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    _add_base_context_arguments(parser)
    add_discord_arguments(parser)


def add_telegram_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_TELEGRAM,
        help=CMD_TELEGRAM_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_TELEGRAM_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    _add_base_context_arguments(parser)
    add_telegram_arguments(parser)


def add_master_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_MASTER,
        help=CMD_MASTER_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_MASTER_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    _add_base_context_arguments(parser)
    add_api_arguments(parser)


def add_worker_parser(subparsers) -> None:
    # noinspection SpellCheckingInspection
    parser = subparsers.add_parser(
        name=CMD_WORKER,
        help=CMD_WORKER_HELP,
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CMD_WORKER_EPILOG,
    )
    assert isinstance(parser, ArgumentParser)
    _add_base_context_arguments(parser)
    add_module_arguments(parser)


def default_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )

    add_dotenv_arguments(parser)

    parser.add_argument(
        "--command-prefix",
        default=get_eval("COMMAND_PREFIX", COMMAND_PREFIX),
        metavar="prefix",
        help=f"Command prefix. (default: '{COMMAND_PREFIX}')",
    )

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

    parser.add_argument(
        "-D",
        action="store_true",
        default=False,
        help="Same as ['-c', '-d', '-vv'] flags",
    )

    subparsers = parser.add_subparsers(dest="cmd")
    add_discord_parser(subparsers)
    add_telegram_parser(subparsers)
    add_master_parser(subparsers)
    add_worker_parser(subparsers)
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
