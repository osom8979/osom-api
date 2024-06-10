# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.msg.worker import MsgWorker
from osom_api.worker.descs import CmdDesc, ParamDesc


class WorkerTestCase(TestCase):
    def test_encode_decode(self):
        param = ParamDesc("param", "param_desc", 10)
        cmd = CmdDesc("cmd", "cmd_desc", [param])
        msg0 = MsgWorker("name", "version", "doc", "path", [cmd])
        data = msg0.encode()
        msg1 = MsgWorker.decode(data)

        self.assertEqual(msg1.name, msg0.name)
        self.assertEqual(msg1.version, msg0.version)
        self.assertEqual(msg1.doc, msg0.doc)
        self.assertEqual(msg1.path, msg0.path)

        self.assertEqual(len(msg0.cmds), 1)
        self.assertEqual(len(msg1.cmds), 1)
        cmd0 = msg0.cmds[0]
        cmd1 = msg1.cmds[0]
        self.assertEqual(cmd0.key, cmd1.key)
        self.assertEqual(cmd0.doc, cmd1.doc)

        self.assertEqual(len(cmd0.params), 1)
        self.assertEqual(len(cmd1.params), 1)
        param0 = cmd0.params[0]
        param1 = cmd1.params[0]
        self.assertEqual(param0.key, param1.key)
        self.assertEqual(param0.doc, param1.doc)
        self.assertEqual(param0.default, param1.default)

    def test_error_case_01(self):
        data = b"\x1f\x8b\x08\x00)\x8eff\x00\xffM\x8cK\x0e\x830\x0cD\xaf\x12y\x8d\x08\xdb\xb2nOQ\xb1\xb0\x12\x97 \x1aL\xe3\xd0\xaaB\xb9;\xee\xbf\xcb\x99\xf7fVp\xd1\x0b\xb4\xc7\x15<;h\xe1\xe0\x02\x9b\x1c\xc8\xb8\x80\xd9D\x12\xc1\x9e\xa0\x82\x91\xeeJI\xa9\x86\x19\x13\xc6\xff\xd5W\xf8\x0cJW\xba\xea\r\xf7t\xc2\xe5\x9c\r\x0bGs\xe34RR\x7f\xc2H\n\xfd\x0b>Os\xd0\xc2>4\x8b\xf3`\x13]\x16\x92l\x7f\xca\x95\x92\x0c<\xa9\xd5\xd4M\xbd\x83\xb2\x01\xab\xddq\x13\xbf\x00\x00\x00"  # noqa
        # ParamDesc.__init__() missing 1 required positional argument: 'default'", '[0]'
        msg = MsgWorker.decode(data)
        self.assertEqual("default", msg.name)
        self.assertEqual("/osom/api/request/default", msg.path)
        self.assertEqual("0.0.9", msg.version)
        self.assertEqual(1, len(msg.cmds))
        self.assertEqual("echo", msg.cmds[0].key)
        self.assertEqual("Echo the chat message", msg.cmds[0].doc)
        self.assertEqual(1, len(msg.cmds[0].params))
        self.assertEqual("message", msg.cmds[0].params[0].key)
        self.assertEqual("", msg.cmds[0].params[0].doc)
        self.assertEqual(None, msg.cmds[0].params[0].default)


if __name__ == "__main__":
    main()
