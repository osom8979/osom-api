# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.args import ModuleArgs
from osom_api.context.base import BaseContextConfig


class WorkerConfig(BaseContextConfig, ModuleArgs):
    def __init__(self, args: Namespace):
        super().__init__(**self.namespace_to_dict(args))
        self.assert_module_properties()
