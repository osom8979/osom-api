# -*- coding: utf-8 -*-

from typing import Annotated, Optional
from unittest import TestCase, main

from osom_api.context.msg import MsgRequest
from osom_api.worker.command import WorkerCommand
from osom_api.worker.metas import ParamMeta
from osom_api.worker.params import (
    ContentParam,
    CreatedAtParam,
    FileParam,
    FilesParam,
    MsgUUIDParam,
    NicknameParam,
    UsernameParam,
)


async def _on_test_callback(
    n0: MsgRequest,
    n1: ContentParam,
    n2: FileParam,
    n3: FilesParam,
    n4: UsernameParam,
    n5: NicknameParam,
    n6: CreatedAtParam,
    n7: MsgUUIDParam,
    n8: Annotated[MsgUUIDParam, "UnsupportedAnnotated"],
    p0,
    p1: Annotated[bool, ParamMeta(name="PP1")],
    p2: Annotated[str, ParamMeta(doc="Doc2", default="Default2")],
    p3: Annotated[int, ParamMeta(doc="Doc3")] = 3,
    p4: Optional[int] = 4,
    p5: int = 5,
    p6=6,
    p7=None,
) -> str:
    """TestDescription"""
    assert all((n0, n1, n2, n3, n4, n5, n6, n7, n8, p0, p1, p2, p3, p4, p5, p6, p7))
    return f"{p1}-{p2}"


class CommandTestCase(TestCase):
    def test_from_callback(self):
        cmd = WorkerCommand.from_callback(_on_test_callback, prefix="_on_")
        self.assertEqual(cmd.key, "test_callback")
        self.assertEqual(cmd.doc, "TestDescription")

        self.assertEqual(len(cmd.params), 8)
        p0 = cmd.params.get("p0")
        p1 = cmd.params.get("PP1")
        p2 = cmd.params.get("p2")
        p3 = cmd.params.get("p3")
        p4 = cmd.params.get("p4")
        p5 = cmd.params.get("p5")
        p6 = cmd.params.get("p6")
        p7 = cmd.params.get("p7")

        self.assertEqual(p0.key, "p0")
        self.assertEqual(p0.doc, "")
        self.assertEqual(p0.default, None)

        self.assertEqual(p1.key, "PP1")
        self.assertEqual(p1.doc, "")
        self.assertEqual(p1.default, None)

        self.assertEqual(p2.key, "p2")
        self.assertEqual(p2.doc, "Doc2")
        self.assertEqual(p2.default, "Default2")

        self.assertEqual(p3.key, "p3")
        self.assertEqual(p3.doc, "Doc3")
        self.assertEqual(p3.default, 3)

        self.assertEqual(p4.key, "p4")
        self.assertEqual(p4.doc, "")
        self.assertEqual(p4.default, 4)

        self.assertEqual(p5.key, "p5")
        self.assertEqual(p5.doc, "")
        self.assertEqual(p5.default, 5)

        self.assertEqual(p6.key, "p6")
        self.assertEqual(p6.doc, "")
        self.assertEqual(p6.default, 6)

        self.assertEqual(p7.key, "p7")
        self.assertEqual(p7.doc, "")
        self.assertEqual(p7.default, None)


if __name__ == "__main__":
    main()
