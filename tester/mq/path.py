# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.mq.path import BROADCAST_BYTES, BROADCAST_PATH, QUEUE_BYTES, QUEUE_PATH


class PathTestCase(TestCase):
    def test_broadcast_path(self):
        self.assertEqual("/osom/api/broadcast", BROADCAST_PATH)
        self.assertEqual(b"/osom/api/broadcast", BROADCAST_BYTES)

    def test_queue_path(self):
        self.assertEqual("/osom/api/queue", QUEUE_PATH)
        self.assertEqual(b"/osom/api/queue", QUEUE_BYTES)


if __name__ == "__main__":
    main()
