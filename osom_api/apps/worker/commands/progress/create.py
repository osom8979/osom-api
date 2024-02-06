# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any

from overrides import override

from osom_api.apps.worker.commands.interface import WorkerCommand
from osom_api.common.context import CommonContext
from osom_api.db.progress import (
    insert_anonymous_progress,
    latest_anonymous_progress_datetime,
)
from osom_api.logging.logging import logger


class ProgressCreate(WorkerCommand):
    __api__ = "/progress/create"

    @override
    async def run(self, data: Any, context: CommonContext) -> Any:
        created = latest_anonymous_progress_datetime(context.supabase)
        if created is not None:
            duration = (datetime.now().astimezone() - created).total_seconds()
            logger.debug(f"Created duration: {duration:.2f}s")

        progress_id = insert_anonymous_progress(context.supabase)
        logger.info(f"Insert progress ID: {progress_id}")
        return {"id": progress_id}
