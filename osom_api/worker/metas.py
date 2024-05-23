# -*- coding: utf-8 -*-

from typing import Any, Optional


class NoDefault:
    pass


class AnnotatedMeta:
    pass


class ParamMeta(AnnotatedMeta):
    def __init__(
        self,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        default: Any = NoDefault,
    ):
        self.name = name
        self.summary = summary
        self.default = default
