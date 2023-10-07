# -*- coding: utf-8 -*-

from sys import exit as sys_exit
from typing import Callable, List, Optional

from osom_api.apps import run_app
from osom_api.arguments import CMDS, PRINTER_ATTR_KEY, get_default_arguments
from osom_api.logging.logging import (
    SEVERITY_NAME_DEBUG,
    add_default_colored_logging,
    add_default_logging,
    add_default_rotate_file_logging,
    add_simple_logging,
    logger,
    set_root_level,
)


def main(
    cmdline: Optional[List[str]] = None,
    printer: Callable[..., None] = print,
    load_dotenv=False,
) -> int:
    args = get_default_arguments(cmdline, load_dotenv=load_dotenv)

    if not hasattr(args, PRINTER_ATTR_KEY):
        setattr(args, PRINTER_ATTR_KEY, printer)

    if not args.cmd:
        printer("The command does not exist")
        return 1

    assert args.cmd in CMDS
    assert isinstance(args.colored_logging, bool)
    assert isinstance(args.default_logging, bool)
    assert isinstance(args.simple_logging, bool)
    assert isinstance(args.rotate_logging_prefix, str)
    assert isinstance(args.rotate_logging_when, str)
    assert isinstance(args.severity, str)
    assert isinstance(args.debug, bool)
    assert isinstance(args.verbose, int)

    cmd = args.cmd
    colored_logging = args.colored_logging
    default_logging = args.default_logging
    simple_logging = args.simple_logging
    rotate_logging_prefix = args.rotate_logging_prefix
    rotate_logging_when = args.rotate_logging_when
    severity = args.severity
    debug = args.debug
    verbose = args.verbose

    if colored_logging:
        add_default_colored_logging()
    elif default_logging:
        add_default_logging()
    elif simple_logging:
        add_simple_logging()

    if rotate_logging_prefix:
        add_default_rotate_file_logging(rotate_logging_prefix, rotate_logging_when)

    if debug:
        set_root_level(SEVERITY_NAME_DEBUG)
    else:
        set_root_level(severity)

    if verbose >= 1:
        logger.debug(f"Arguments: {args}")

    return run_app(cmd, args)


if __name__ == "__main__":
    sys_exit(main())
