import unittest

from imap_codec import (
    LineEnding,
    LineFragmentInfo,
    LiteralAnnouncement,
    LiteralFragmentInfo,
    LiteralMode,
)


class TestLineFragmentInfo(unittest.TestCase):
    def test_start(self):
        start = 17
        info = LineFragmentInfo(start=start, end=71)
        self.assertEqual(info.start, start)

    def test_end(self):
        end = 71
        info = LineFragmentInfo(start=17, end=end)
        self.assertEqual(info.end, end)

    def test_announcement(self):
        info = LineFragmentInfo(start=17, end=71)
        self.assertEqual(info.announcement, None)

        announcement = LiteralAnnouncement(LiteralMode.Sync, length=42)
        info = LineFragmentInfo(start=17, end=71, announcement=announcement)
        self.assertEqual(info.announcement, announcement)

    def test_ending(self):
        info = LineFragmentInfo(start=17, end=71)
        self.assertEqual(info.ending, LineEnding.CrLf)

        ending = LineEnding.Lf
        info = LineFragmentInfo(start=17, end=71, ending=ending)
        self.assertEqual(info.ending, ending)

    def test_repr(self):
        start = 17
        end = 71
        announcement = LiteralAnnouncement(LiteralMode.Sync, length=42)
        ending = LineEnding.Lf
        default_ending = LineEnding.CrLf
        info1 = LineFragmentInfo(start=start, end=end)
        info2 = LineFragmentInfo(
            start=start, end=end, announcement=announcement, ending=ending
        )
        self.assertEqual(str(info1), f"({start}, {end}, None, {default_ending})")
        self.assertEqual(str(info2), f"({start}, {end}, {announcement}, {ending})")

    def test_str(self):
        start = 17
        end = 71
        announcement = LiteralAnnouncement(LiteralMode.Sync, length=42)
        ending = LineEnding.Lf
        default_ending = LineEnding.CrLf
        info1 = LineFragmentInfo(start=start, end=end)
        info2 = LineFragmentInfo(
            start=start, end=end, announcement=announcement, ending=ending
        )
        self.assertEqual(
            repr(info1),
            f"LineFragmentInfo(start={start}, end={end}, announcement=None, ending={default_ending!r})",
        )
        self.assertEqual(
            repr(info2),
            f"LineFragmentInfo(start={start}, end={end}, announcement={announcement!r}, ending={ending!r})",
        )

    def test_eq(self):
        info1 = LineFragmentInfo(start=17, end=71)
        info2 = LineFragmentInfo(start=17, end=71)
        info3 = LineFragmentInfo(
            start=42,
            end=71,
            announcement=LiteralAnnouncement(LiteralMode.Sync, length=42),
        )
        info4 = LineFragmentInfo(start=17, end=42, ending=LineEnding.Lf)

        self.assertEqual(info1, info1)
        self.assertEqual(info1, info2)
        self.assertNotEqual(info1, info3)
        self.assertNotEqual(info1, info4)

        self.assertEqual(info2, info1)
        self.assertEqual(info2, info2)
        self.assertNotEqual(info2, info3)
        self.assertNotEqual(info2, info4)

        self.assertNotEqual(info3, info1)
        self.assertNotEqual(info3, info2)
        self.assertEqual(info3, info3)
        self.assertNotEqual(info3, info4)

        self.assertNotEqual(info4, info1)
        self.assertNotEqual(info4, info2)
        self.assertNotEqual(info4, info3)
        self.assertEqual(info4, info4)


class TestLiteralFragmentInfo(unittest.TestCase):
    def test_start(self):
        start = 17
        info = LiteralFragmentInfo(start=start, end=71)
        self.assertEqual(info.start, start)

    def test_end(self):
        end = 71
        info = LiteralFragmentInfo(start=17, end=end)
        self.assertEqual(info.end, end)

    def test_repr(self):
        start = 17
        end = 71
        info = LiteralFragmentInfo(start=start, end=end)
        self.assertEqual(str(info), f"({start}, {end})")

    def test_str(self):
        start = 17
        end = 71
        info = LiteralFragmentInfo(start=start, end=end)
        self.assertEqual(repr(info), f"LiteralFragmentInfo(start={start}, end={end})")

    def test_eq(self):
        info1 = LiteralFragmentInfo(start=17, end=71)
        info2 = LiteralFragmentInfo(start=17, end=71)
        info3 = LiteralFragmentInfo(start=42, end=71)

        self.assertEqual(info1, info1)
        self.assertEqual(info1, info2)
        self.assertNotEqual(info1, info3)

        self.assertEqual(info2, info1)
        self.assertEqual(info2, info2)
        self.assertNotEqual(info2, info3)

        self.assertNotEqual(info3, info1)
        self.assertNotEqual(info3, info2)
        self.assertEqual(info3, info3)
