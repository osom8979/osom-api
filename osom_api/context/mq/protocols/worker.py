# -*- coding: utf-8 -*-

from dataclasses import dataclass
from io import StringIO
from typing import List

from type_serialize import decode, encode
from type_serialize.byte.byte_coder import DEFAULT_BYTE_CODING_TYPE
from type_serialize.variables import COMPRESS_LEVEL_TRADEOFF

from osom_api.commands import COMMAND_PREFIX
from osom_api.worker.descs import CmdDesc


@dataclass
class RegisterWorker:
    name: str
    version: str
    doc: str
    path: str
    cmds: List[CmdDesc]

    def encode(self, level=COMPRESS_LEVEL_TRADEOFF, coding=DEFAULT_BYTE_CODING_TYPE):
        return encode(self, level=level, coding=coding)

    @classmethod
    def decode(cls, data: bytes, coding=DEFAULT_BYTE_CODING_TYPE):
        result = decode(data, cls=cls, coding=coding)
        assert isinstance(result, cls)
        return result

    def as_help(self, command_prefix=COMMAND_PREFIX) -> str:
        buffer = StringIO()
        buffer.write(f"{self.name} ({self.version})\n")
        buffer.write(self.doc + "\n")
        for cmd in self.cmds:
            buffer.write(f"  {command_prefix}{cmd.key} - {cmd.doc}\n")
            for param in cmd.params:
                buffer.write(f"    - {param.key}[{param.default}] - {param.doc}")
        return buffer.getvalue()
