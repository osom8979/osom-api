# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.worker.descs import CmdDesc, ParamDesc


class DescTestCase(TestCase):
    def test_isinstance_desc(self):
        self.assertIsInstance(CmdDesc("", "", list()), tuple)
        self.assertIsInstance(ParamDesc("", "", None), tuple)


if __name__ == "__main__":
    main()
