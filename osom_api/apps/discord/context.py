# -*- coding: utf-8 -*-

from argparse import Namespace

from discord import Intents
from discord.ext.commands import Bot, check
from discord.ext.commands.context import Context as CommandContext
from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.discord.config import DiscordConfig
from osom_api.arguments import version as osom_version
from osom_api.context.context import CommonContext
from osom_api.db.discord_register import registered_discord_channel_id
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
            command_prefix="?",
            intents=self._intents,
            sync_command=True,
            application_id=self._config.discord_application_id,
        )

        def is_registration():
            async def predicate(ctx):
                return await self.is_registration(ctx)

            return check(predicate)

        @bot.command(help="Shows osom version number")
        @is_registration()
        async def version(ctx) -> None:
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

    async def is_registration(self, ctx: CommandContext) -> bool:
        if await registered_discord_channel_id(self.supabase, ctx.channel.id):
            return True

        logger.error(f"Unregistered channel {ctx.channel.id}")
        link = "https://www.osom.run/"
        await ctx.send(f"Not registered. Go to {link} and sign up!")
        return False

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
