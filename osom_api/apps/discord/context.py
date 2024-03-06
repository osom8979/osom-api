# -*- coding: utf-8 -*-

from argparse import Namespace

from discord import Intents
from discord.ext.commands import Bot
from discord.ext.commands.context import Context as CommandContext
from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.discord.config import DiscordConfig
from osom_api.arguments import version as osom_version
from osom_api.context.context import CommonContext
from osom_api.logging.logging import logger


class DiscordContext(CommonContext):
    def __init__(self, args: Namespace):
        self._config = DiscordConfig.from_namespace(args)
        super().__init__(self._config)

        self._osom_version = osom_version()
        self._intents = Intents.default()
        self._intents.typing = False
        self._intents.presences = False
        self._intents.message_content = True
        self._bot = bot = Bot(
            command_prefix="$",
            intents=self._intents,
            sync_command=True,
            application_id=self._config.discord_application_id,
        )

        @bot.command(help="Shows osom version number")
        async def version(ctx: CommandContext) -> None:
            await self.on_version(ctx)

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

    async def on_version(self, ctx: CommandContext) -> None:
        await ctx.send(self._osom_version)

    async def main(self) -> None:
        await self.open_common_context()
        try:
            await self._bot.start(token=self._config.discord_token)
        finally:
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
