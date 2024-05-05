# -*- coding: utf-8 -*-

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from osom_api.arguments import CMD_MASTER, get_default_arguments


class ArgumentsTestCase(TestCase):
    def test_load_dotenv(self):
        with TemporaryDirectory() as tmpdir:
            dotenv_path = Path(tmpdir) / ".dotenv"
            dotenv_path.write_text("VERBOSE=20")
            self.assertTrue(dotenv_path.is_file())

            cmdline = ["--dotenv-path", str(dotenv_path), CMD_MASTER]
            args = get_default_arguments(cmdline)
            self.assertFalse(hasattr(args, "no_dotenv"))
            self.assertFalse(hasattr(args, "dotenv_path"))
            self.assertEqual(args.cmd, CMD_MASTER)
            self.assertEqual(args.verbose, 20)


if __name__ == "__main__":
    main()
