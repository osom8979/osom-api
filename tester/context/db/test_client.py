# -*- coding: utf-8 -*-

from typing import Optional, Tuple
from unittest import IsolatedAsyncioTestCase, main, skipIf

from dotenv import dotenv_values

from osom_api.context.db import DbClient
from tester import get_root_dotenv_local_path


def get_dotenv_supabase_values() -> Optional[Tuple[str, str]]:
    values = dotenv_values(get_root_dotenv_local_path())
    url = values.get("NEXT_PUBLIC_SUPABASE_URL")
    key = values.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url, key
    else:
        return None


@skipIf(
    get_dotenv_supabase_values() is None,
    "An environment variable for SUPABASE is not defined",
)
class DbClientTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        values = get_dotenv_supabase_values()
        self.assertIsNotNone(values)
        url, key = values
        self.db = DbClient(url, key)

    async def asyncSetUp(self):
        await self.db.open()

    async def asyncTearDown(self):
        await self.db.close()

    async def test_get_members(self):
        members = await self.db.get_members()
        self.assertIsNotNone(members)
        self.assertGreaterEqual(len(members.data), 1)


if __name__ == "__main__":
    main()
