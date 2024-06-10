# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace
from io import StringIO
from typing import Annotated, Final, Iterable, Union

from openai import AsyncOpenAI
from openai.types import ChatModel
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from overrides import override

from osom_api.arguments import version as osom_version
from osom_api.exceptions import MsgError
from osom_api.logging.logging import logger
from osom_api.system.environ import get_typed_environ_value
from osom_api.worker.base import WorkerBase
from osom_api.worker.metas import ParamMeta
from osom_api.worker.params import BodyParam, MsgUUIDParam

PROG: Final[str] = "gpt"
DESCRIPTION: Final[str] = "Worker module for OpenAI's ChatGPT"
VERSION: Final[str] = osom_version()

DEFAULT_TIMEOUT: Final[float] = 120.0
DEFAULT_MODEL: Final[str] = "gpt-4o"


def get_default_arguments(*args):
    parser = ArgumentParser(prog=PROG, description=DESCRIPTION)
    parser.add_argument(
        "--openai-api-key",
        default=get_typed_environ_value("OPENAI_API_KEY"),
        metavar="key",
        help="OpenAI API Key",
    )
    parser.add_argument(
        "--openai-timeout",
        default=get_typed_environ_value("OPENAI_TIMEOUT", DEFAULT_TIMEOUT),
        metavar="sec",
        type=float,
        help=f"OpenAI timeout. (default: {DEFAULT_TIMEOUT:.2f})",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    return parser.parse_known_args(args, Namespace())[0]


class GptWorker(WorkerBase):
    _openai: AsyncOpenAI

    def __init__(self):
        super().__init__(PROG, VERSION, DESCRIPTION)
        self.register_command(self.on_gpt)

    @override
    def init(self, *args) -> None:
        super().init(*args)

        namespace = get_default_arguments(*args)
        logger.debug(f"GptWorker arguments: {namespace}")

        assert isinstance(namespace.openai_api_key, str)
        assert isinstance(namespace.openai_timeout, float)
        api_key = namespace.openai_api_key
        timeout = namespace.openai_timeout
        self._openai = AsyncOpenAI(api_key=api_key, timeout=timeout)

    async def on_gpt(
        self,
        n: Annotated[int, ParamMeta(doc="Number of chat completions", default=1)],
        model: Annotated[str, ParamMeta(doc="Chat model name", default=DEFAULT_MODEL)],
        msg_uuid: MsgUUIDParam,
        body: BodyParam,
    ) -> str:
        """Talk to OpenAI's ChatGPT"""

        if n < 1:
            raise MsgError(msg_uuid, "The 'n' argument must be 1 or greater")
        if not model:
            raise MsgError(msg_uuid, "The 'model' argument is empty")
        if not body:
            raise MsgError(msg_uuid, "The 'body' is empty")

        messages = [{"role": "user", "content": body}]
        request = dict(messages=messages, model=model, n=n)
        response = dict()

        try:
            chat_completion = await self.create_chat_completion(
                messages=messages,  # type: ignore[arg-type]
                model=model,
                n=n,
            )
            assert len(chat_completion.choices) == n

            reply_buffer = StringIO()
            if len(chat_completion.choices) == 1:
                reply_buffer.write(chat_completion.choices[0].message.content)
            elif len(chat_completion.choices) >= 2:
                choice = chat_completion.choices[0]
                reply_buffer.write("[0] " + choice.message.content)
                for i, choice in enumerate(chat_completion.choices[1:]):
                    reply_buffer.write(f"\n[{i + 1}] " + choice.message.content)
            else:
                assert False, "Inaccessible section"
            reply_text = reply_buffer.getvalue()

            response.update(chat_completion.model_dump())
            return reply_text
        except BaseException as e:
            error_message = "OpenAI API request failed"
            response.update(
                error_type=type(e).__name__,
                error_message=error_message,
                msg_uuid=msg_uuid,
            )
            raise MsgError(msg_uuid, error_message) from e
        finally:
            await self.context.db.insert_openai_chat(msg_uuid, request, response)
            logger.debug(f"Msg({msg_uuid}) Insert OpenAI chat results")

    async def create_chat_completion(
        self,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str, ChatModel],
        n=1,
    ):
        """
        :param messages:
            The messages to generate chat completions for, in the chat format.
        :param model:
            ID of the model to use.
        :param n:
            How many chat completion choices to generate for each input message.
        """

        return await self._openai.chat.completions.create(
            messages=messages,
            model=model,
            n=n,
        )


__worker__ = GptWorker()
