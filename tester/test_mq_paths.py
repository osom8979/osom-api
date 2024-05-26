# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.mq_paths import (
    BROADCAST_PATH,
    PATH_ROOT,
    PATH_SEPARATOR,
    QUEUE_DEFAULT_PATH,
    QUEUE_PATH,
    RESPONSE_PATH,
)


class MqPathsTestCase(TestCase):
    def test_path_root(self):
        self.assertEqual(f"{PATH_SEPARATOR}osom{PATH_SEPARATOR}api", PATH_ROOT)

    def test_path_root_starts_with(self):
        self.assertTrue(PATH_ROOT.startswith(PATH_SEPARATOR))
        self.assertTrue(QUEUE_PATH.startswith(PATH_ROOT))
        self.assertTrue(QUEUE_DEFAULT_PATH.startswith(QUEUE_PATH))
        self.assertTrue(RESPONSE_PATH.startswith(PATH_ROOT))
        self.assertTrue(BROADCAST_PATH.startswith(PATH_ROOT))


if __name__ == "__main__":
    main()
