# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.context.db.mixins import members, progress


class DbMixinsBaseTestCase(TestCase):
    def test_members(self):
        self.assertEqual(members.T.members, "members")
        self.assertEqual(members.C.member, "member")
        self.assertEqual(members.C.team, "team")
        self.assertEqual(members.C.role, "role")

    def test_progress(self):
        self.assertEqual(progress.T.progress, "progress")
        self.assertEqual(progress.C.id, "id")
        self.assertEqual(progress.C.owner, "owner")
        self.assertEqual(progress.C.value, "value")
        self.assertEqual(progress.C.expired_at, "expired_at")
        self.assertEqual(progress.C.created_at, "created_at")
        self.assertEqual(progress.C.updated_at, "updated_at")
        self.assertEqual(
            progress.R.increase_anonymous_progress_value,
            "increase_anonymous_progress_value",
        )
        self.assertEqual(progress.R.progress_id, "progress_id")
        self.assertEqual(progress.R.increase_value, "increase_value")
        self.assertEqual(progress.V.null, "null")


if __name__ == "__main__":
    main()
