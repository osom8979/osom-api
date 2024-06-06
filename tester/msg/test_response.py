# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.msg.response import MsgResponse


class ResponseTestCase(TestCase):
    def test_encode_decode(self):
        msg0 = MsgResponse("unknown_uuid", content="content")
        data = msg0.encode()
        msg1 = MsgResponse.decode(data)

        self.assertEqual(msg1.msg_uuid, msg0.msg_uuid)
        self.assertEqual(msg1.content, msg0.content)
        self.assertEqual(msg1.error, msg0.error)
        self.assertEqual(msg1.files, msg0.files)
        self.assertEqual(msg1.created_at, msg0.created_at)


if __name__ == "__main__":
    main()
