# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.context.mq.protocol.worker import (
    WORKER_REQUEST_API_KEY,
    WORKER_REQUEST_DATA_KEY,
    WORKER_REQUEST_MSG_KEY,
    Keys,
)


class WorkerTestCase(TestCase):
    def test_keys(self):
        self.assertEqual(Keys.api, WORKER_REQUEST_API_KEY)
        self.assertEqual(Keys.msg, WORKER_REQUEST_MSG_KEY)
        self.assertEqual(Keys.data, WORKER_REQUEST_DATA_KEY)


if __name__ == "__main__":
    main()
