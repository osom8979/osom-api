# -*- coding: utf-8 -*-

from unittest import TestCase, main

from osom_api.worker.replys import ContentReply


class ReplysTestCase(TestCase):
    def test_content_reply(self):
        self.assertEqual(ContentReply, str)

        content = ContentReply("test")
        self.assertIsInstance(content, ContentReply)
        self.assertIsInstance(content, str)
        self.assertEqual(content, "test")


if __name__ == "__main__":
    main()
