# -*- coding: utf-8 -*-

from typing import Dict, Union


def create_error_object(
    code: Union[None, str, int],
    details: Union[None, str, int],
    hint: Union[None, str, int],
    message: Union[None, str, int],
) -> Dict[str, Union[None, str, int]]:
    return dict(
        code=code,
        details=details,
        hint=hint,
        message=message,
    )
