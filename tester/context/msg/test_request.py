# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.context.msg.request import MsgProvider, MsgRequest


class RequestTestCase(TestCase):
    def test_encode_decode(self):
        msg0 = MsgRequest(MsgProvider.tester, content="content")
        data = msg0.encode()
        msg1 = MsgRequest.decode(data)
        self.assertEqual(msg1.provider, msg1.provider)
        self.assertEqual(msg1.message_id, msg1.message_id)
        self.assertEqual(msg1.channel_id, msg1.channel_id)
        self.assertEqual(msg1.content, msg1.content)
        self.assertEqual(msg1.username, msg1.username)
        self.assertEqual(msg1.nickname, msg1.nickname)
        self.assertEqual(msg1.files, msg1.files)
        self.assertEqual(msg1.created_at, msg1.created_at)
        self.assertEqual(msg1.msg_uuid, msg1.msg_uuid)


if __name__ == "__main__":
    main()
