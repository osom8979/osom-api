# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Optional

# noinspection PyPackageRequirements
from uvicorn.config import LoopSetupType

from osom_api.args import ApiArgs
from osom_api.context.base import BaseContextConfig


class MasterConfig(BaseContextConfig, ApiArgs):
    def __init__(self, args: Namespace):
        super().__init__(**self.namespace_to_dict(args))
        self.assert_api_properties()

    @property
    def loop_setup_type(self) -> LoopSetupType:
        return "uvloop" if self.use_uvloop else "asyncio"

    @property
    def opt_api_token(self) -> Optional[str]:
        return None if self.api_disable_auth else self.api_token

    @property
    def opt_api_openapi_url(self) -> Optional[str]:
        return None if self.api_disable_docs else self.api_openapi_url
