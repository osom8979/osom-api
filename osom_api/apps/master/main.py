# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.apps.master.context import MasterContext


def master_main(args: Namespace) -> None:
    MasterContext(args).run()
