# -*- coding: utf-8 -*-

from aiogram.filters import Command


class CommandHelp(Command):
    def __init__(self):
        super().__init__("help")
