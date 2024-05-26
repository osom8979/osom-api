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
        self.assertSequenceEqual(msg1.cmds, msg0.cmds)


if __name__ == "__main__":
    main()
