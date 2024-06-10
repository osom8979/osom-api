# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace
from typing import Annotated, Final, Iterable, Union

from openai import AsyncOpenAI
from openai.types import ChatModel
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from overrides import override

from osom_api.arguments import version as osom_version
from osom_api.system.environ import get_typed_environ_value
from osom_api.worker.base import WorkerBase
from osom_api.worker.metas import ParamMeta

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
    async def open(self, *args, **kwargs) -> None:
        await super().open(*args, **kwargs)

        namespace = get_default_arguments(*args)
        assert isinstance(namespace.openai_api_key, str)
        assert isinstance(namespace.openai_timeout, float)
        api_key = namespace.openai_api_key
        timeout = namespace.openai_timeout
        self._openai = AsyncOpenAI(api_key=api_key, timeout=timeout)

    @override
    async def close(self) -> None:
        await super().close()

    async def on_gpt(
        self,
        n: Annotated[int, ParamMeta(doc="Number of chat completions", default=1)],
        model: Annotated[str, ParamMeta(doc="Chat model name", default=DEFAULT_MODEL)],
    ) -> str:
        """Talk to OpenAI's ChatGPT."""

        assert self is not None
        return f"{model}-{n}"

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
