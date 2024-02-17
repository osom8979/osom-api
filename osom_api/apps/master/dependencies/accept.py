# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import Header, status
from fastapi.datastructures import Optional
from fastapi.exceptions import HTTPException


async def compatible_application_json(accept: Annotated[Optional[str], Header()]):
    if not accept:
        # 'None' is considered acceptable.
        return True

    tokens = accept.replace(" ", "").lower().split(",")
    for token in tokens:
        mime = token.split(";")[0]
        if mime in ("application/json", "application/*", "*/*"):
            return True

    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
