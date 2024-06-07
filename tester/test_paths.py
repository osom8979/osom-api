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


class PathsTestCase(TestCase):
    def test_mq_root_path(self):
        self.assertEqual(f"{PATH_SEPARATOR}osom{PATH_SEPARATOR}api", MQ_ROOT_PATH)

    def test_mq_msg_paths(self):
        self.assertEqual(MQ_REQUEST_PATH, join_path(MQ_ROOT_PATH, "request"))
        self.assertEqual(MQ_RESPONSE_PATH, join_path(MQ_ROOT_PATH, "response"))

    def test_mq_broadcast_paths(self):
        self.assertEqual(MQ_BROADCAST_PATH, join_path(MQ_ROOT_PATH, "broadcast"))

    def test_mq_register_paths(self):
        self.assertEqual(MQ_REGISTER_PATH, join_path(MQ_ROOT_PATH, "register"))
        self.assertEqual(MQ_REGISTER_WORKER_PATH, join_path(MQ_REGISTER_PATH, "worker"))
        self.assertEqual(
            MQ_REGISTER_WORKER_REQUEST_PATH,
            join_path(MQ_REGISTER_WORKER_PATH, "request"),
        )

    def test_mq_unregister_paths(self):
        self.assertEqual(MQ_UNREGISTER_PATH, join_path(MQ_ROOT_PATH, "unregister"))
        self.assertEqual(
            MQ_UNREGISTER_WORKER_PATH,
            join_path(MQ_UNREGISTER_PATH, "worker"),
        )


if __name__ == "__main__":
    main()
