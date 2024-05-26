# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.context.mq.protocols.worker import RegisterWorker
from osom_api.worker.descs import CmdDesc, ParamDesc


class WorkerTestCase(TestCase):
    def test_encode_decode(self):
        param = ParamDesc("param", "param_desc", 10)
        cmd = CmdDesc("cmd", "cmd_desc", [param])
        msg0 = RegisterWorker("name", "version", "doc", "path", [cmd])
        data = msg0.encode()
        msg1 = RegisterWorker.decode(data)

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


if __name__ == "__main__":
    main()
