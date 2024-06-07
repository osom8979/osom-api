# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.protocols.msg.enums.provider import MsgProvider
from osom_api.protocols.msg.request import MsgRequest


class RequestTestCase(TestCase):
    def test_encode_decode(self):
        msg0 = MsgRequest(
            MsgProvider.tester,
            content="/chat,model=gpt-4o,n=1 your_message",
        )
        data = msg0.encode()
        msg1 = MsgRequest.decode(data)

        self.assertEqual(msg1.provider, msg0.provider)
        self.assertEqual(msg1.message_id, msg0.message_id)
        self.assertEqual(msg1.channel_id, msg0.channel_id)
        self.assertEqual(msg1.content, msg0.content)
        self.assertEqual(msg1.username, msg0.username)
        self.assertEqual(msg1.nickname, msg0.nickname)
        self.assertEqual(msg1.files, msg0.files)
        self.assertEqual(msg1.created_at, msg0.created_at)
        self.assertEqual(msg1.msg_uuid, msg0.msg_uuid)
        self.assertEqual(msg1._msg_cmd, msg0._msg_cmd)


if __name__ == "__main__":
    main()
