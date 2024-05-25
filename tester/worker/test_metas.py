# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.worker.metas import AnnotatedMeta, ParamMeta


class MetasTestCase(TestCase):
    def test_isinstance_meta(self):
        self.assertIsInstance(ParamMeta(), AnnotatedMeta)


if __name__ == "__main__":
    main()
