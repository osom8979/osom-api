# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any

from overrides import override

from osom_api.apps.worker.commands.interface import WorkerCommand
from osom_api.common.context import CommonContext
from osom_api.logging.logging import logger


class ProgressCreate(WorkerCommand):
    __api__ = "/progress/create"

    @override
    async def run(self, data: Any, context: CommonContext) -> Any:
        response = (
            context.supabase.table("progress")
            .select("created_at")
            .is_("owner", "null")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if len(response.data) >= 1:
            created_at = datetime.fromisoformat(response.data[0]["created_at"])
            created_duration = (
                datetime.now().astimezone() - created_at
            ).total_seconds()
            logger.debug(f"Created duration: {created_duration:.2f}s")

        response = context.supabase.table("progress").insert({"value": 0}).execute()
        progress_id = response.data[0]["id"]
        logger.info(f"Insert progress ID: {progress_id}")
        return {"id": progress_id}
