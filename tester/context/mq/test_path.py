# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.arguments import DEFAULT_REQUEST_PATH
from osom_api.context.mq.path import (
    BROADCAST_PATH,
    PATH_ROOT,
    PATH_SEPARATOR,
    QUEUE_DEFAULT_PATH,
    QUEUE_PATH,
    RESPONSE_PATH,
    encode_path,
    join_path,
)


class PathTestCase(TestCase):
    def test_path_root(self):
        self.assertEqual(f"{PATH_SEPARATOR}osom{PATH_SEPARATOR}api", PATH_ROOT)

    def test_broadcast_path(self):
        self.assertEqual("/osom/api/broadcast", BROADCAST_PATH)
        self.assertEqual(b"/osom/api/broadcast", encode_path(BROADCAST_PATH))

    def test_join_path(self):
        self.assertEqual(QUEUE_PATH, join_path(PATH_ROOT, "queue"))
        self.assertEqual(QUEUE_DEFAULT_PATH, join_path(QUEUE_PATH, "default"))
        self.assertEqual(RESPONSE_PATH, join_path(PATH_ROOT, "response"))
        self.assertEqual(BROADCAST_PATH, join_path(PATH_ROOT, "broadcast"))

    def test_default_variables(self):
        self.assertEqual(DEFAULT_REQUEST_PATH, QUEUE_DEFAULT_PATH)


if __name__ == "__main__":
    main()
