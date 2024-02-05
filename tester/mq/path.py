# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.mq.path import BROADCAST_BYTES, BROADCAST_PATH


class PathTestCase(TestCase):
    def test_broadcast_path(self):
        self.assertEqual("/osom/api/broadcast", BROADCAST_PATH)
        self.assertEqual(b"/osom/api/broadcast", BROADCAST_BYTES)


if __name__ == "__main__":
    main()
