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
from osom_api.commands import COMMAND_PREFIX
from osom_api.context import Context
from osom_api.context.msg import MsgFile, MsgProvider, MsgRequest
from osom_api.logging.logging import logger


class DiscordContext(Context):
    def __init__(self, args: Namespace):
        self._config = DiscordConfig.from_namespace(args)
        super().__init__(self._config)

        self._intents = Intents.all()
        self._intents.members = False
        self._intents.message_content = True
        self._intents.presences = False
        self._intents.typing = False
        self._bot = bot = Bot(
            command_prefix=COMMAND_PREFIX,
            help_command=None,
            intents=self._intents,
            application_id=self._config.discord_application_id,
            sync_command=True,
        )

        def is_registration():
            async def predicate(ctx):
                return await self.is_registration(ctx)

            return check(predicate)

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

    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        files = list()
        for attach in message.attachments:
            content = await attach.read()
            content_type = attach.content_type if attach.content_type else ""
            image_width = attach.width if attach.width else 0
            image_height = attach.height if attach.height else 0
            msg_file = MsgFile(
                content_type=content_type,
                file_id=str(attach.id),
                file_name=attach.filename,
                file_size=attach.size,
                image_width=image_width,
                image_height=image_height,
                content=content,
            )
            files.append(msg_file)

        author = message.author
        global_name = author.global_name if author.global_name else author.name
        msg = MsgRequest(
            provider=MsgProvider.Discord,
            message_id=message.id,
            channel_id=message.channel.id,
            username=author.name,
            nickname=global_name,
            text=message.content,
            created_at=message.created_at,
            files=files,
        )

        response = await self.do_message(msg)
        if response is None:
            return

        await message.channel.send(response.reply_content)

    async def main(self) -> None:
        await self.open_common_context()
        try:
            await self._bot.start(token=self._config.discord_token)
        finally:
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
