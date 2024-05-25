# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase, main

from osom_api.worker.params import (
    ContentParam,
    CreatedAtParam,
    FileParam,
    FilesParam,
    MsgUUIDParam,
    NicknameParam,
    Param,
    UsernameParam,
)


class ParamsTestCase(TestCase):
    def test_datetime_eq(self):
        now = datetime.now()
        self.assertEqual(CreatedAtParam.from_datetime(now), now)

    def test_isinstance_param(self):
        self.assertIsInstance(ContentParam(), Param)
        self.assertIsInstance(FileParam(), Param)
        self.assertIsInstance(FilesParam(), Param)
        self.assertIsInstance(UsernameParam(), Param)
        self.assertIsInstance(NicknameParam(), Param)
        self.assertIsInstance(CreatedAtParam.now(), Param)
        self.assertIsInstance(MsgUUIDParam(), Param)

        self.assertIsInstance(ContentParam(), str)
        self.assertIsInstance(FilesParam(), list)
        self.assertIsInstance(UsernameParam(), str)
        self.assertIsInstance(NicknameParam(), str)
        self.assertIsInstance(CreatedAtParam.now(), datetime)
        self.assertIsInstance(MsgUUIDParam(), str)


if __name__ == "__main__":
    main()
