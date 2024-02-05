# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.apps.worker.context import WorkerContext


def worker_main(args: Namespace) -> None:
    WorkerContext(args).run()
