# -*- coding: utf-8 -*-

from aiogram.filters import Command


class CommandVersion(Command):
    def __init__(self):
        super().__init__("version")
