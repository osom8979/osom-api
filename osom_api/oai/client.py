# -*- coding: utf-8 -*-

from typing import Optional

from openai import AsyncOpenAI

from osom_api.arguments import DEFAULT_OPENAI_TIMEOUT
from osom_api.exceptions import NotInitializedError


class OaiClient:
    _openai: Optional[AsyncOpenAI]

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout=DEFAULT_OPENAI_TIMEOUT,
    ):
        if api_key:
            self._openai = AsyncOpenAI(api_key=api_key, timeout=timeout)
        else:
            self._openai = None

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        self._openai = None

    @property
    def openai(self) -> AsyncOpenAI:
        if self._openai is None:
            raise NotInitializedError("Client is not initialized")
        return self._openai

    async def create_chat_completion(self, content: str):
        return await self.openai.chat.completions.create(
            messages=[{"role": "user", "content": content}],
            model="gpt-4",
        )
