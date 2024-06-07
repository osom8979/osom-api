# -*- coding: utf-8 -*-


class OsomApiError(Exception):
    pass


class PollingTimeoutError(OsomApiError):
    pass


class PacketLoadError(OsomApiError):
    pass


class EmptyApiError(OsomApiError):
    pass


class InvalidCommandError(OsomApiError):
    pass


class InvalidParameterError(OsomApiError):
    pass


class CommandRuntimeError(OsomApiError):
    pass


class InvalidMessageIdError(OsomApiError):
    pass


class NoMessageIdError(OsomApiError):
    pass


class NoMessageDataError(OsomApiError):
    pass


class PacketDumpError(OsomApiError):
    pass


class InsertError(OsomApiError):
    def __init__(self, table_name: str):
        super().__init__(f"Failed to insert row into table '{table_name}'")


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


class MsgError(OsomApiError):
    def __init__(self, msg_uuid: str, *args):
        super().__init__(*args)
        self.msg_uuid = msg_uuid


class NotACoroutineError(OsomApiError):
    pass
