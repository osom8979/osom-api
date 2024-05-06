# -*- coding: utf-8 -*-

from unittest import IsolatedAsyncioTestCase, main, skipIf

from dotenv import dotenv_values

from osom_api.context.mq import MqClient
from tester import get_root_dotenv_local_path


def get_dotenv_redis_url():
    return dotenv_values(get_root_dotenv_local_path()).get("REDIS_URL")


@skipIf(get_dotenv_redis_url() is None, "Undefined REDIS_URL environment variable")
class MqClientTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mq = MqClient(get_dotenv_redis_url())

    async def asyncSetUp(self):
        await self.mq.open()

    async def asyncTearDown(self):
        await self.mq.close()

    async def test_ping(self):
        self.assertTrue(await self.mq.ping())


if __name__ == "__main__":
    main()
