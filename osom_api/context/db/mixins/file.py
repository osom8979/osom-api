# -*- coding: utf-8 -*-

from typing import Optional

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables
from osom_api.exceptions import InsertError


class T(Tables):
    file = AutoName()


class C(Columns):
    id = AutoName()
    provider = AutoName()
    storage = AutoName()
    name = AutoName()  # type: ignore[assignment]
    content_type = AutoName()
    native_id = AutoName()
    created_at = AutoName()
    updated_at = AutoName()


class File(DbMixinBase):
    async def select_file(self, file_uuid: str):
        return (
            await self.supabase.table(T.file).select("*").eq(C.id, file_uuid).execute()
        )

    async def insert_file(
        self,
        file_uuid: str,
        provider: str,
        storage: str,
        name: Optional[str] = None,
        content_type: Optional[str] = None,
        native_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> None:
        obj = {
            C.id: file_uuid,
            C.provider: provider,
            C.storage: storage,
            C.name: name,
            C.content_type: content_type,
            C.native_id: native_id,
        }
        if created_at:
            obj[C.created_at] = created_at

        response = await self.supabase.table(T.file).insert(obj).execute()

        if len(response.data) == 0:
            raise InsertError(T.file)

        assert len(response.data) == 1
        assert response.data[0][C.id] == file_uuid
