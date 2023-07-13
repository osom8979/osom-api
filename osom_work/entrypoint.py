# -*- coding: utf-8 -*-

from sys import exit as sys_exit
from typing import Callable, List, Optional

from osom_work.apps.bot.main import bot_main
from osom_work.apps.health.main import health_main
from osom_work.apps.master.main import master_main
from osom_work.apps.worker.main import worker_main
from osom_work.arguments import (
    CMD_BOT,
    CMD_HEALTH,
    CMD_MASTER,
    CMD_WORKER,
    CMDS,
    get_default_arguments,
)
from osom_work.logging.logging import (
    SEVERITY_NAME_DEBUG,
    logger,
    set_colored_formatter_logging_config,
    set_root_level,
    set_simple_logging_config,
)


def main(
    cmdline: Optional[List[str]] = None,
    printer: Callable[..., None] = print,
) -> int:
    args = get_default_arguments(cmdline)

    if not args.cmd:
        printer("The command does not exist")
        return 1

    if args.colored_logging and args.simple_logging:
        printer("The 'colored_logging' and 'simple_logging' flags cannot coexist")
        return 1

    cmd = args.cmd
    colored_logging = args.colored_logging
    simple_logging = args.simple_logging
    severity = args.severity
    debug = args.debug
    verbose = args.verbose

    assert cmd in CMDS
    assert isinstance(colored_logging, bool)
    assert isinstance(simple_logging, bool)
    assert isinstance(severity, str)
    assert isinstance(debug, bool)
    assert isinstance(verbose, int)

    if colored_logging:
        set_colored_formatter_logging_config()
    elif simple_logging:
        set_simple_logging_config()

    if debug:
        set_root_level(SEVERITY_NAME_DEBUG)
    else:
        set_root_level(severity)

    logger.debug(f"Arguments: {args}")

    main_func = {
        CMD_BOT: bot_main,
        CMD_HEALTH: health_main,
        CMD_MASTER: master_main,
        CMD_WORKER: worker_main,
    }

    try:
        main_func[cmd](args, printer)
    except BaseException as e:
        logger.exception(e)
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys_exit(main())
