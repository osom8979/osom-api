# -*- coding: utf-8 -*-


class WorkerError(Exception):
    pass


class PollingTimeoutError(WorkerError):
    pass


class PacketLoadError(WorkerError):
    pass


class EmptyApiError(WorkerError):
    pass


class NotFoundCommandKeyError(WorkerError):
    pass


class CommandRuntimeError(WorkerError):
    pass


class NoMessageIdError(WorkerError):
    pass


class PacketDumpError(WorkerError):
    pass
