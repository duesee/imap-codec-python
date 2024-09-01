import unittest

from imap_codec import LiteralMode


class TestLiteralMode(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(repr(LiteralMode.Sync), "LiteralMode.Sync")
        self.assertEqual(repr(LiteralMode.NonSync), "LiteralMode.NonSync")

    def test_str(self):
        self.assertEqual(str(LiteralMode.Sync), "LiteralMode.Sync")
        self.assertEqual(str(LiteralMode.NonSync), "LiteralMode.NonSync")

    def test_eq(self):
        self.assertEqual(LiteralMode.Sync, LiteralMode.Sync)
        self.assertEqual(LiteralMode.NonSync, LiteralMode.NonSync)
        self.assertNotEqual(LiteralMode.Sync, LiteralMode.NonSync)
        self.assertNotEqual(LiteralMode.NonSync, LiteralMode.Sync)
