# -*- coding: utf-8 -*-

from argparse import Namespace

from discord import Intents
from discord.ext.commands import Bot, check
from discord.ext.commands.context import Context as CommandContext
from discord.message import Message

from osom_api.aio.run import aio_run
from osom_api.apps.discord.config import DiscordConfig
from osom_api.arguments import NOT_REGISTERED_MSG
from osom_api.commands import COMMAND_PREFIX
from osom_api.context.endpoint import EndpointContext
from osom_api.logging.logging import logger
from osom_api.protocols.msg import MsgFile, MsgProvider, MsgRequest


class DiscordContext(EndpointContext):
    def __init__(self, args: Namespace):
        self._config = DiscordConfig.from_namespace(args)
        super().__init__(MsgProvider.discord, self._config)

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
