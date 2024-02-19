# -*- coding: utf-8 -*-

from argparse import Namespace
from asyncio.exceptions import CancelledError
from functools import lru_cache
from typing import Callable, Dict

from osom_api.apps.master.main import master_main
from osom_api.apps.telegram.main import telegram_main
from osom_api.apps.worker.main import worker_main
from osom_api.arguments import CMD_MASTER, CMD_TELEGRAM, CMD_WORKER
from osom_api.logging.logging import logger


@lru_cache
def cmd_apps() -> Dict[str, Callable[[Namespace], None]]:
    return {
        CMD_TELEGRAM: telegram_main,
        CMD_MASTER: master_main,
        CMD_WORKER: worker_main,
    }


def run_app(cmd: str, args: Namespace) -> int:
    apps = cmd_apps()
    app = apps.get(cmd, None)
    if app is None:
        logger.error(f"Unknown app command: {cmd}")
        return 1

    try:
        app(args)
    except CancelledError:
        logger.debug("An cancelled signal was detected")
    except KeyboardInterrupt:
        logger.warning("An interrupt signal was detected")
    except BaseException as e:
        logger.exception(e)
        return 1

    return 0
