# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_work.apps.master.context import Context


def master_main(args: Namespace) -> None:
    Context(args).run()
