# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.protocols.msg.cmd import MsgCmd


class CmdTestCase(TestCase):
    def test_eq(self):
        cmd0 = MsgCmd.from_content("/chat,model=test,n=2 TEMP")
        cmd1 = MsgCmd("chat", {"model": "test", "n": "2"}, "TEMP")
        self.assertEqual(cmd0, cmd1)

    def test_from_text(self):
        cmd0 = MsgCmd.from_content("/chat,model=gpt-4o,n=1 your_body")
        self.assertEqual("chat", cmd0.command)
        self.assertDictEqual({"model": "gpt-4o", "n": "1"}, cmd0.kwargs)
        self.assertEqual("your_body", cmd0.body)

        self.assertEqual("gpt-4o", cmd0.get("model"))
        self.assertEqual(1, cmd0.get("n", 0))

    def test_encode_decode(self):
        cmd0 = MsgCmd("chat", {"model": "test", "n": "1"}, "body")
        data = cmd0.encode()
        cmd1 = MsgCmd.decode(data)

        self.assertEqual(cmd1.command, cmd0.command)
        self.assertDictEqual(cmd1.kwargs, cmd0.kwargs)
        self.assertEqual(cmd1.body, cmd0.body)


if __name__ == "__main__":
    main()
