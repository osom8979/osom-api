# -*- coding: utf-8 -*-

from typing import Iterable, Optional, Union

from openai import AsyncOpenAI
from openai.types import ChatModel
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from osom_api.arguments import DEFAULT_CHAT_MODEL, DEFAULT_OPENAI_TIMEOUT
from osom_api.exceptions import NotInitializedError


def create_async_openai(
    api_key: Optional[str] = None,
    timeout: Optional[float] = None,
) -> Optional[AsyncOpenAI]:
    if api_key:
        return AsyncOpenAI(api_key=api_key, timeout=timeout)
    else:
        return None


class OaiClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout=DEFAULT_OPENAI_TIMEOUT,
        default_chat_model: Union[str, ChatModel] = DEFAULT_CHAT_MODEL,
    ):
        self._openai = create_async_openai(api_key, timeout)
        self.default_chat_model = default_chat_model

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        self._openai = None

    @property
    def openai(self) -> AsyncOpenAI:
        if self._openai is None:
            raise NotInitializedError("Client is not initialized")
        return self._openai

    async def create_chat_completion(
        self,
        messages: Iterable[ChatCompletionMessageParam],
        model: Optional[Union[str, ChatModel]] = None,
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

        return await self.openai.chat.completions.create(
            messages=messages,
            model=model if model else self.default_chat_model,
            n=n,
        )
