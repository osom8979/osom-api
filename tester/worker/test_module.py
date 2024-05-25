# -*- coding: utf-8 -*-

from unittest import IsolatedAsyncioTestCase, main

from osom_api.context.msg import MsgProvider, MsgRequest, MsgResponse
from osom_api.worker.module import Module
from tester.worker.modules import tester


class ModuleTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.fake_context = object()
        self.module = Module(tester, isolate=True)

    async def asyncSetUp(self):
        self.assertTrue(self.module.has_open)
        self.assertFalse(self.module.opened)
        await self.module.open(self.fake_context)
        self.assertTrue(self.module.opened)

    async def asyncTearDown(self):
        self.assertTrue(self.module.opened)
        self.assertTrue(self.module.has_close)
        await self.module.close()
        self.assertFalse(self.module.opened)

    async def test_run(self):
        req = MsgRequest(provider=MsgProvider.tester, content="/tester")
        res = await self.module.run(req)
        self.assertIsInstance(res, MsgResponse)
        self.assertEqual(res.content, "1-2")


if __name__ == "__main__":
    main()
