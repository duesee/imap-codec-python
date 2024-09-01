import unittest

from imap_codec import LineEnding


class TestLineEnding(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(repr(LineEnding.Lf), "LineEnding.Lf")
        self.assertEqual(repr(LineEnding.CrLf), "LineEnding.CrLf")

    def test_str(self):
        self.assertEqual(str(LineEnding.Lf), "LineEnding.Lf")
        self.assertEqual(str(LineEnding.CrLf), "LineEnding.CrLf")

    def test_eq(self):
        self.assertEqual(LineEnding.Lf, LineEnding.Lf)
        self.assertEqual(LineEnding.CrLf, LineEnding.CrLf)
        self.assertNotEqual(LineEnding.Lf, LineEnding.CrLf)
        self.assertNotEqual(LineEnding.CrLf, LineEnding.Lf)
