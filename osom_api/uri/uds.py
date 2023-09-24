# -*- coding: utf-8 -*-

from typing import Final

UNIX_URI_PREFIX: Final[str] = "unix:"
"""Prefix of UDS(Unix Domain Socket).
"""

UNIX_ABSTRACT_URI_PREFIX: Final[str] = "unix-abstract:"
"""Prefix of UDS(Unix Domain Socket) in abstract namespace.
"""


def is_uds_family(address: str) -> bool:
    """
    Make sure it is a Unix Domain Socket (UDS) address.
    """
    if address.startswith(UNIX_URI_PREFIX):
        return True
    if address.startswith(UNIX_ABSTRACT_URI_PREFIX):
        return True
    return False
