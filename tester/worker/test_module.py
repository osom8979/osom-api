# -*- coding: utf-8 -*-

from unittest import IsolatedAsyncioTestCase, main

from osom_api.context.msg import MsgProvider, MsgRequest, MsgResponse
from osom_api.worker.module import Module
from osom_api.worker.modules import tester


class ModuleTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.fake_context = object()
        self.module = Module(tester, isolate=True)

    async def asyncSetUp(self):
        self.assertTrue(self.module.has_open)
        await self.module.open(self.fake_context)

    async def asyncTearDown(self):
        self.assertTrue(self.module.has_close)
        await self.module.close()

    async def test_run(self):
        req = MsgRequest(provider=MsgProvider.tester)
        res = await self.module.run(req)
        self.assertIsInstance(res, MsgResponse)


if __name__ == "__main__":
    main()
