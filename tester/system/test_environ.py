# -*- coding: utf-8 -*-

import os
from typing import Final
from unittest import TestCase, main

from osom_api.system.environ import environ_dict, exchange_env

TEST_RECC_HTTP_BIND: Final[str] = "TEST_RECC_HTTP_BIND"


class EnvironTestCase(TestCase):
    def test_get_os_envs_dict(self):
        envs = environ_dict()
        self.assertIsInstance(envs, dict)
        self.assertLess(0, len(envs["PATH"]))

    def test_exchange_env(self):
        change_value = "1.2.3.4"
        original_http_bind_1 = os.environ.get(TEST_RECC_HTTP_BIND)
        original_http_bind_2 = exchange_env(TEST_RECC_HTTP_BIND, change_value)
        self.assertEqual(original_http_bind_1, original_http_bind_2)

        changed_http_bind_1 = os.environ.get(TEST_RECC_HTTP_BIND)
        self.assertEqual(change_value, changed_http_bind_1)

        changed_http_bind_2 = exchange_env(TEST_RECC_HTTP_BIND, original_http_bind_2)
        self.assertEqual(change_value, changed_http_bind_2)

        original_http_bind_3 = os.environ.get(TEST_RECC_HTTP_BIND)
        self.assertEqual(original_http_bind_1, original_http_bind_3)


if __name__ == "__main__":
    main()
