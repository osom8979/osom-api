# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any

from overrides import override

from osom_api.apps.worker.commands.interface import WorkerCommand
from osom_api.db.progress import (
    insert_anonymous_progress,
    latest_anonymous_progress_datetime,
)
from osom_api.logging.logging import logger
from osom_api.mq.protocol.worker import CreateProgressResponse


class ProgressCreate(WorkerCommand):
    @override
    async def run(self, data: Any) -> CreateProgressResponse:
        created = await latest_anonymous_progress_datetime(self.supabase)
        if created is not None:
            duration = (datetime.now().astimezone() - created).total_seconds()
            logger.debug(f"Created duration: {duration:.2f}s")

        body = await insert_anonymous_progress(self.supabase)
        logger.info(f"Insert progress ID: {body.id}")
        return CreateProgressResponse(id=body.id)
