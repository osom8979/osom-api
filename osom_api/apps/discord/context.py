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
from osom_api.context.mq.path import encode_path
from osom_api.context.mq.protocols.worker import RegisterWorker
from osom_api.context.msg import MsgFile, MsgProvider, MsgRequest
from osom_api.logging.logging import logger
from osom_api.mq_paths import (
    BROADCAST_PATH,
    REGISTER_WORKER_PATH,
    REGISTER_WORKER_REQUEST_PATH,
)


class DiscordContext(Context):
    def __init__(self, args: Namespace):
        self._config = DiscordConfig.from_namespace(args)
        self._broadcast_path = encode_path(BROADCAST_PATH)
        self._register_worker_path = encode_path(REGISTER_WORKER_PATH)
        subscribe_paths = self._broadcast_path, self._register_worker_path
        super().__init__(config=self._config, subscribe_paths=subscribe_paths)

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

    async def publish_register_worker_request(self) -> None:
        await self.publish(REGISTER_WORKER_REQUEST_PATH, MsgProvider.discord.encode())
        logger.info("Published register worker request packet!")

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")
        await self.publish_register_worker_request()

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")
        if self._register_worker_path == channel:
            worker_info = RegisterWorker.decode(data)

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
            msg_file = MsgFile(
                provider=MsgProvider.discord,
                native_id=str(attach.id),
                name=attach.filename,
                content=content,
                content_type=attach.content_type,
                width=attach.width,
                height=attach.height,
                created_at=message.created_at,
            )
            files.append(msg_file)

        msg = MsgRequest(
            provider=MsgProvider.discord,
            message_id=message.id,
            channel_id=message.channel.id,
            content=message.content,
            username=message.author.name,
            nickname=message.author.global_name,
            files=files,
            created_at=message.created_at,
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
