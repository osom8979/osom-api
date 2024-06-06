# -*- coding: utf-8 -*-

from typing import Annotated, Optional
from unittest import IsolatedAsyncioTestCase, main

from osom_api.msg import MsgProvider, MsgRequest, MsgResponse
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


class CommandTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.cmd = WorkerCommand.from_callback(self._on_test_callback, prefix="_on_")
        self.msg_params = list()

    async def _on_test_callback(
        self,
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
        self.msg_params = [n0, n1, n2, n3, n4, n5, n6, n7, n8]
        return f"{p0},{p1},{p2},{p3},{p4},{p5},{p6},{p7}"

    def test_default(self):
        self.assertEqual(self.cmd.key, "test_callback")
        self.assertEqual(self.cmd.doc, "TestDescription")

    async def test_callable(self):
        req = MsgRequest(
            provider=MsgProvider.tester,
            content="/test_callback,p0=kk,PP1=True,p3=0 [content]",
            username="tester",
        )
        res = await self.cmd(req)
        self.assertIsInstance(res, MsgResponse)
        self.assertEqual(res.content, "kk,True,Default2,0,4,5,6,None")

        self.assertEqual(len(self.msg_params), 9)
        self.assertIsInstance(self.msg_params[0], MsgRequest)
        self.assertEqual(self.msg_params[1], "[content]")
        self.assertIsNone(self.msg_params[2], None)
        self.assertListEqual(self.msg_params[3], list())
        self.assertEqual(self.msg_params[4], "tester")
        self.assertIsNone(self.msg_params[5], None)
        self.assertEqual(self.msg_params[6], req.created_at)
        self.assertEqual(self.msg_params[7], req.msg_uuid)
        self.assertEqual(self.msg_params[8], req.msg_uuid)

    def test_params(self):
        self.assertEqual(len(self.cmd.params), 8)
        p0 = self.cmd.params.get("p0")
        p1 = self.cmd.params.get("p1")
        p2 = self.cmd.params.get("p2")
        p3 = self.cmd.params.get("p3")
        p4 = self.cmd.params.get("p4")
        p5 = self.cmd.params.get("p5")
        p6 = self.cmd.params.get("p6")
        p7 = self.cmd.params.get("p7")

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
