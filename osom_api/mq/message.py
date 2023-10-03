# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import Any, Dict, Final, Sequence


@unique
class MessageType(Enum):
    subscribe = auto()
    unsubscribe = auto()
    psubscribe = auto()
    punsubscribe = auto()
    message = auto()
    pmessage = auto()


MESSAGE_TYPE_NAMES: Final[Sequence[str]] = tuple(mt.name for mt in MessageType)


@dataclass
class Message:
    type: MessageType
    pattern: str
    channel: Any
    data: Any

    @property
    def is_subscribe(self) -> bool:
        return self.type == MessageType.subscribe

    @property
    def is_unsubscribe(self) -> bool:
        return self.type == MessageType.unsubscribe

    @property
    def is_psubscribe(self) -> bool:
        return self.type == MessageType.psubscribe

    @property
    def is_punsubscribe(self) -> bool:
        return self.type == MessageType.punsubscribe

    @property
    def is_message(self) -> bool:
        return self.type == MessageType.message

    @property
    def is_pmessage(self) -> bool:
        return self.type == MessageType.pmessage

    @property
    def has_pattern(self) -> bool:
        return len(self.pattern) >= 1

    @classmethod
    def from_message(cls, msg: Dict[str, Any]):
        if not isinstance(msg, dict):
            raise TypeError("The type of message must be 'dict' type")

        if "type" not in msg:
            raise KeyError("The 'type' attribute is required")
        if "pattern" not in msg:
            raise KeyError("The 'pattern' attribute is required")
        if "channel" not in msg:
            raise KeyError("The 'channel' attribute is required")
        if "data" not in msg:
            raise KeyError("The 'data' attribute is required")

        msg_type = msg["type"]
        msg_pattern = msg["pattern"]
        msg_channel = msg["channel"]
        msg_data = msg["data"]

        if not isinstance(msg_type, str):
            raise TypeError("The type of message['type'] must be 'str' type")
        if not isinstance(msg_pattern, (type(None), str)):
            raise TypeError("The type of message['pattern'] must be None or 'str' type")

        if msg_type not in MESSAGE_TYPE_NAMES:
            raise ValueError(f"Unknown message type: '{msg_type}'")

        return cls(
            getattr(MessageType, msg_type),
            msg_pattern if msg_pattern else str(),
            msg_channel,
            msg_data,
        )
