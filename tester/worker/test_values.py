# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.worker.values import NoDefault


class ValuesTestCase(TestCase):
    def test_no_default(self):
        self.assertNotEqual(NoDefault, None)


if __name__ == "__main__":
    main()
