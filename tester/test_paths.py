# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.paths import (
    MQ_BROADCAST_PATH,
    MQ_REGISTER_PATH,
    MQ_REGISTER_WORKER_PATH,
    MQ_REGISTER_WORKER_REQUEST_PATH,
    MQ_REQUEST_PATH,
    MQ_RESPONSE_PATH,
    MQ_ROOT_PATH,
    MQ_UNREGISTER_PATH,
    MQ_UNREGISTER_WORKER_PATH,
)
from osom_api.utils.path.join import PATH_SEPARATOR, join_path
from osom_api.utils.path.mq import encode_path


class PathsTestCase(TestCase):
    def test_mq_root_path(self):
        self.assertEqual(f"{PATH_SEPARATOR}osom{PATH_SEPARATOR}api", MQ_ROOT_PATH)

    def test_mq_paths(self):
        self.assertEqual(MQ_REQUEST_PATH, join_path(MQ_ROOT_PATH, "request"))
        self.assertEqual(MQ_RESPONSE_PATH, join_path(MQ_ROOT_PATH, "response"))
        self.assertEqual(MQ_BROADCAST_PATH, join_path(MQ_ROOT_PATH, "broadcast"))
        self.assertEqual(MQ_REGISTER_PATH, join_path(MQ_ROOT_PATH, "register"))
        self.assertEqual(MQ_UNREGISTER_PATH, join_path(MQ_ROOT_PATH, "unregister"))

        self.assertEqual(
            MQ_REGISTER_WORKER_PATH,
            join_path(MQ_REGISTER_PATH, "worker"),
        )
        self.assertEqual(
            MQ_REGISTER_WORKER_REQUEST_PATH,
            join_path(MQ_REGISTER_WORKER_PATH, "request"),
        )
        self.assertEqual(
            MQ_UNREGISTER_WORKER_PATH,
            join_path(MQ_UNREGISTER_PATH, "worker"),
        )

    def test_broadcast_path(self):
        self.assertEqual("/osom/api/broadcast", MQ_BROADCAST_PATH)
        self.assertEqual(b"/osom/api/broadcast", encode_path(MQ_BROADCAST_PATH))


if __name__ == "__main__":
    main()
