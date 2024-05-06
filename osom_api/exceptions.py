# -*- coding: utf-8 -*-


class OsomApiError(Exception):
    pass


class PollingTimeoutError(OsomApiError):
    pass


class PacketLoadError(OsomApiError):
    pass


class EmptyApiError(OsomApiError):
    pass


class NotFoundCommandKeyError(OsomApiError):
    pass


class CommandRuntimeError(OsomApiError):
    pass


class NoMessageIdError(OsomApiError):
    pass


class NoMessageDataError(OsomApiError):
    pass


class PacketDumpError(OsomApiError):
    pass


class InsertError(OsomApiError):
    pass


class UnregisteredError(OsomApiError):
    pass


class InvalidStateError(OsomApiError):
    pass


class NotInitializedError(OsomApiError):
    pass


class AlreadyInitializedError(OsomApiError):
    pass


class InvalidArgumentError(OsomApiError):
    pass
