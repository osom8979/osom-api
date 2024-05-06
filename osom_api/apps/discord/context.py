# -*- coding: utf-8 -*-

from argparse import Namespace

from discord import Intents
from discord.ext.commands import Bot, check
from discord.ext.commands.context import Context as CommandContext
from discord.message import Message
from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.discord.config import DiscordConfig
from osom_api.arguments import NOT_REGISTERED_MSG
from osom_api.arguments import version as osom_version
from osom_api.context import Context
from osom_api.logging.logging import logger


class DiscordContext(Context):
    def __init__(self, args: Namespace):
        self._config = DiscordConfig.from_namespace(args)
        super().__init__(self._config)

        self._osom_version = osom_version()
        self._intents = Intents.default()
        self._intents.typing = False
        self._intents.presences = False
        self._intents.message_content = True
        self._bot = bot = Bot(
            command_prefix="/",
            help_command=None,
            intents=self._intents,
            application_id=self._config.discord_application_id,
            sync_command=True,
        )

        def is_registration():
            async def predicate(ctx):
                return await self.is_registration(ctx)

            return check(predicate)

        @bot.command(help="Shows osom-api version number")
        @is_registration()
        async def version(ctx) -> None:
            await self.on_version(ctx)

        @bot.event
        @is_registration()
        async def on_message(message) -> None:
            await self.on_message(message)

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
        if await self.db.registered_discord_channel_id(ctx.channel.id):
            return True

        logger.error(f"Unregistered channel {ctx.channel.id}")
        await ctx.send(NOT_REGISTERED_MSG)
        return False

    async def on_version(self, ctx: CommandContext) -> None:
        await ctx.send(self._osom_version)

    async def on_message(self, message: Message) -> None:
        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")
        o = dict(
            content_type=message.type,
            message_id=message.id,
            chat=message.channel.id,
            username=message.author.name,
            nickname=message.author.global_name,
            content=message.content,
            created_at=message.created_at,
        )
        for attach in message.attachments:
            if attach.content_type == "image/png":
                po = dict(
                    file_id=attach.id,
                    width=attach.width,
                    height=attach.height,
                    file_size=attach.size,
                    filename=attach.filename,
                    # proxy_url=attach.proxy_url,
                    url=attach.url,
                    temporary=attach.ephemeral,
                )

    async def main(self) -> None:
        await self.open_common_context()
        try:
            await self._bot.start(token=self._config.discord_token)
        finally:
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
