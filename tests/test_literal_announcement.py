import unittest

from imap_codec import LiteralAnnouncement, LiteralMode


class TestLiteralAnnouncement(unittest.TestCase):
    def test_mode(self):
        mode = LiteralMode.Sync
        announcement = LiteralAnnouncement(mode, length=42)
        self.assertEqual(announcement.mode, mode)

    def test_length(self):
        length = 42
        announcement = LiteralAnnouncement(LiteralMode.Sync, length=length)
        self.assertEqual(announcement.length, length)

    def test_str(self):
        mode = LiteralMode.Sync
        length = 42
        announcement = LiteralAnnouncement(mode, length=length)
        self.assertEqual(str(announcement), f"({mode}, {length})")

    def test_repr(self):
        mode = LiteralMode.Sync
        length = 42
        announcement = LiteralAnnouncement(mode, length=length)
        self.assertEqual(
            repr(announcement), f"LiteralAnnouncement({mode!r}, length={length})"
        )

    def test_eq(self):
        announcement1 = LiteralAnnouncement(LiteralMode.Sync, length=42)
        announcement2 = LiteralAnnouncement(LiteralMode.Sync, length=42)
        announcement3 = LiteralAnnouncement(LiteralMode.NonSync, length=42)
        announcement4 = LiteralAnnouncement(LiteralMode.NonSync, length=71)

        self.assertEqual(announcement1, announcement1)
        self.assertEqual(announcement1, announcement2)
        self.assertNotEqual(announcement1, announcement3)
        self.assertNotEqual(announcement1, announcement4)

        self.assertEqual(announcement2, announcement1)
        self.assertEqual(announcement2, announcement2)
        self.assertNotEqual(announcement2, announcement3)
        self.assertNotEqual(announcement2, announcement4)

        self.assertNotEqual(announcement3, announcement1)
        self.assertNotEqual(announcement3, announcement2)
        self.assertEqual(announcement3, announcement3)
        self.assertNotEqual(announcement3, announcement4)

        self.assertNotEqual(announcement4, announcement1)
        self.assertNotEqual(announcement4, announcement2)
        self.assertNotEqual(announcement4, announcement3)
        self.assertEqual(announcement4, announcement4)
