# -*- coding: utf-8 -*-

from functools import lru_cache
from os.path import abspath, dirname
from pathlib import Path


@lru_cache
def get_root_path() -> Path:
    return Path(abspath(dirname(__file__))).parent


@lru_cache
def get_root_dotenv_local_path() -> Path:
    return get_root_path() / ".env.local"
