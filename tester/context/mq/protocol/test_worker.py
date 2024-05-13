# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.context.mq.protocol.worker import (
    WORKER_REQUEST_CMD_KEY,
    WORKER_REQUEST_DATA_KEY,
    WORKER_REQUEST_ID_KEY,
    Keys,
)


class WorkerTestCase(TestCase):
    def test_keys(self):
        self.assertEqual("id", WORKER_REQUEST_ID_KEY)
        self.assertEqual("cmd", WORKER_REQUEST_CMD_KEY)
        self.assertEqual("data", WORKER_REQUEST_DATA_KEY)

        self.assertEqual(Keys.id, WORKER_REQUEST_ID_KEY)
        self.assertEqual(Keys.cmd, WORKER_REQUEST_CMD_KEY)
        self.assertEqual(Keys.data, WORKER_REQUEST_DATA_KEY)


if __name__ == "__main__":
    main()
