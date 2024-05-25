# -*- coding: utf-8 -*-

from typing import Any, Optional

from osom_api.worker.values import NoDefault


class AnnotatedMeta:
    pass


class ParamMeta(AnnotatedMeta):
    def __init__(
        self,
        name: Optional[str] = None,
        doc: Optional[str] = None,
        default: Any = NoDefault,
    ):
        self.name = name
        self.doc = doc
        self.default = default
