# -*- coding: utf-8 -*-

from argparse import Namespace
from asyncio.exceptions import CancelledError
from functools import lru_cache

from osom_work.apps.bot.main import bot_main
from osom_work.apps.health.main import health_main
from osom_work.apps.master.main import master_main
from osom_work.apps.worker.main import worker_main
from osom_work.arguments import CMD_BOT, CMD_HEALTH, CMD_MASTER, CMD_WORKER
from osom_work.logging.logging import logger


@lru_cache
def cmd_apps():
    return {
        CMD_BOT: bot_main,
        CMD_HEALTH: health_main,
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
        return 0
    except KeyboardInterrupt:
        logger.warning("An interrupt signal was detected")
        return 0
    except Exception as e:
        logger.exception(e)
        return 1
    except BaseException as e:
        logger.exception(e)
        return 1
    else:
        return 0
