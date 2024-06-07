# -*- coding: utf-8 -*-

from io import BytesIO
from signal import SIGINT, raise_signal
from typing import AnyStr, Iterable, Optional, Sequence

from overrides import override

from osom_api.config import Config
from osom_api.context.db import DbClient
from osom_api.context.mq import MqClient, MqClientCallback
from osom_api.context.oai import OaiClient
from osom_api.context.s3 import S3Client
from osom_api.logging.logging import logger
from osom_api.msg import MsgFile, MsgFlow, MsgRequest, MsgResponse, MsgStorage


class Context(MqClientCallback):
    def __init__(
        self,
        config: Config,
        *,
        subscribe_paths: Optional[Sequence[AnyStr]] = None,
    ):
        self._mq = MqClient(
            url=config.redis_url,
            connection_timeout=config.redis_connection_timeout,
            subscribe_timeout=config.redis_subscribe_timeout,
            close_timeout=config.redis_close_timeout,
            redis_expire_short=config.redis_expire_short,
            redis_expire_medium=config.redis_expire_medium,
            redis_expire_long=config.redis_expire_long,
            callback=self,
            done=None,
            task_name=None,
            ssl_cert_reqs="none",
            subscribe_paths=subscribe_paths,
            debug=config.debug,
            verbose=config.verbose,
        )
        self._db = DbClient(
            supabase_url=config.supabase_url,
            supabase_key=config.supabase_key,
            auto_refresh_token=True,
            persist_session=True,
            postgrest_client_timeout=config.supabase_postgrest_timeout,
            storage_client_timeout=config.supabase_storage_timeout,
        )
        self._s3 = S3Client(
            endpoint=config.s3_endpoint,
            access=config.s3_access,
            secret=config.s3_secret,
            region=config.s3_region,
            bucket=config.s3_bucket,
        )
        self._oai = OaiClient(
            api_key=config.openai_api_key,
            timeout=config.openai_timeout,
            default_chat_model=config.openai_default_chat_model,
        )

        self.command_prefix = config.command_prefix
        self.debug = config.debug
        self.verbose = config.verbose

    @property
    def mq(self):
        return self._mq

    @property
    def db(self):
        return self._db

    @property
    def s3(self):
        return self._s3

    @property
    def oai(self):
        return self._oai

    async def open_common_context(self) -> None:
        await self._mq.open()
        await self._db.open()
        await self._s3.open()
        await self._oai.open()

    async def close_common_context(self) -> None:
        await self._oai.close()
        await self._s3.close()
        await self._db.close()
        await self._mq.close()

    @staticmethod
    def raise_interrupt_signal() -> None:
        raise_signal(SIGINT)

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("The Redis subscription task is completed")

    async def publish(self, key: str, data: bytes) -> None:
        await self._mq.publish(key, data)

    async def upload_msg_file(
        self,
        file: MsgFile,
        msg_uuid: str,
        flow: MsgFlow,
        storage=MsgStorage.r2,
    ) -> None:
        if file.content is None:
            raise BufferError("Empty file content")

        await self._s3.upload_data(
            data=BytesIO(file.content),
            key=file.path,
            content_type=file.content_type,
        )
        logger.info(f"Successfully uploaded file to S3: '{file.path}'")

        await self._db.insert_file(
            file_uuid=file.file_uuid,
            provider=file.provider,
            storage=storage,
            name=file.name,
            content_type=file.content_type,
            native_id=file.native_id,
            created_at=file.created_at.isoformat(),
        )
        logger.info(
            "Successfully inserted file info to DB: "
            f"'{file.file_uuid}' -> '{file.path}'"
        )

        await self._db.insert_msg2file(
            msg_uuid=msg_uuid,
            file_uuid=file.file_uuid,
            flow=flow,
        )
        logger.info(
            "Successfully inserted msg2file info to DB: "
            f"'{msg_uuid}' -> {file.file_uuid}"
        )

    async def upload_msg_files(
        self,
        files: Iterable[MsgFile],
        msg_uuid: str,
        flow: MsgFlow,
        storage=MsgStorage.r2,
    ) -> None:
        for file in files:
            await self.upload_msg_file(file, msg_uuid, flow, storage)

    async def upload_msg_request(self, message: MsgRequest) -> None:
        await self._db.insert_msg(
            msg_uuid=message.msg_uuid,
            provider=message.provider,
            message_id=message.message_id,
            channel_id=message.channel_id,
            username=message.username,
            nickname=message.nickname,
            content=message.content,
            created_at=message.created_at.isoformat(),
        )
        logger.info(f"Successfully inserted msg_request to DB: '{message.msg_uuid}'")

        await self.upload_msg_files(
            files=message.files,
            msg_uuid=message.msg_uuid,
            flow=MsgFlow.request,
        )

    async def upload_msg_response(self, message: MsgResponse) -> None:
        await self._db.insert_reply(
            msg=message.msg_uuid,
            content=message.content,
            error=message.error,
            created_at=message.created_at.isoformat(),
        )
        logger.info(f"Successfully inserted msg_response to DB: '{message.msg_uuid}'")

        await self.upload_msg_files(
            files=message.files,
            msg_uuid=message.msg_uuid,
            flow=MsgFlow.response,
        )

    # async def on_cmd_chat(self, message: MsgRequest) -> MsgResponse:
    #     msg_uuid = message.msg_uuid
    #     cmd_arg = message.msg_cmd
    #     n = cmd_arg.get("n", 1)
    #     model = cmd_arg.get("model", self._oai.default_chat_model)
    #
    #     if n < 1:
    #         raise MsgError(msg_uuid, "The 'n' argument must be 1 or greater")
    #     if not model:
    #         raise MsgError(msg_uuid, "The 'model' argument is empty")
    #     if not message.content:
    #         raise MsgError(msg_uuid, "The content is empty")
    #
    #     messages = [{"role": "user", "content": message.content}]
    #     request = dict(messages=messages, model=model, n=n)
    #     response = dict()
    #
    #     try:
    #         chat_completion = await self.oai.create_chat_completion(
    #             messages, model, n
    #         )
    #         assert len(chat_completion.choices) == n
    #
    #         reply_buffer = StringIO()
    #         if len(chat_completion.choices) == 1:
    #             reply_buffer.write(chat_completion.choices[0].message.content)
    #         elif len(chat_completion.choices) >= 2:
    #             choice = chat_completion.choices[0]
    #             reply_buffer.write("[0] " + choice.message.content)
    #             for i, choice in enumerate(chat_completion.choices[1:]):
    #                 reply_buffer.write(f"\n[{i + 1}] " + choice.message.content)
    #         else:
    #             assert False, "Inaccessible section"
    #         reply_text = reply_buffer.getvalue()
    #
    #         response.update(chat_completion.model_dump())
    #         return MsgResponse(msg_uuid, reply_text)
    #     except BaseException as e:
    #         error_message = "OpenAI API request failed"
    #         response.update(
    #             error_type=type(e).__name__,
    #             error_message=error_message,
    #             msg_uuid=message.msg_uuid,
    #         )
    #         raise MsgError(msg_uuid, error_message) from e
    #     finally:
    #         await self._db.insert_openai_chat(msg_uuid, request, response)
    #         logger.debug(f"Msg({msg_uuid}) Insert OpenAI chat results")
