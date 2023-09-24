# -*- coding: utf-8 -*-

from typing import Final, NamedTuple, Optional

NOT_FOUND_INDEX: Final[int] = -1

OPENING_PORT: Final[str] = ":"
OPENING_PORT_LEN: Final[int] = len(OPENING_PORT)

OPENING_IPV6: Final[str] = "["
OPENING_IPV6_LEN: Final[int] = len(OPENING_IPV6)

CLOSING_IPV6: Final[str] = "]"
CLOSING_IPV6_LEN: Final[int] = len(CLOSING_IPV6)


class HostPort(NamedTuple):
    host: str
    port: Optional[int]


def parse_ipv4_or_domain_port(address: str) -> HostPort:
    opening_port_index = address.rfind(OPENING_PORT)
    if opening_port_index == NOT_FOUND_INDEX:
        return HostPort(address, None)

    host_end = opening_port_index
    port_begin = opening_port_index + OPENING_PORT_LEN

    host = address[:host_end]
    port = int(address[port_begin:])
    return HostPort(host, port)


def parse_ipv6_port(address: str) -> HostPort:
    if not address.startswith(OPENING_IPV6):
        raise ValueError("IPv6 requires `opening square brackets`")

    closing_ipv6_index = address.find(CLOSING_IPV6)
    if closing_ipv6_index == NOT_FOUND_INDEX:
        raise ValueError("IPv6 requires `closing square brackets`")

    opening_port_index = address.find(OPENING_PORT, closing_ipv6_index)
    if opening_port_index == NOT_FOUND_INDEX:
        return HostPort(address, None)

    host_end = closing_ipv6_index + CLOSING_IPV6_LEN
    port_begin = opening_port_index + OPENING_PORT_LEN

    host = address[:host_end]
    port = int(address[port_begin:])
    return HostPort(host, port)


def parse_host_port(address: str) -> HostPort:
    if address.startswith(OPENING_IPV6):
        return parse_ipv6_port(address)
    else:
        return parse_ipv4_or_domain_port(address)
