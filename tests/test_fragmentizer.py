import unittest

from imap_codec import (
    AuthenticateData,
    Command,
    DecodeFailed,
    DecodeIncomplete,
    Fragmentizer,
    FragmentizerMessagePoisonedError,
    FragmentizerMessageTooLongError,
    Greeting,
    IdleDone,
    LineEnding,
    LineFragmentInfo,
    LiteralAnnouncement,
    LiteralFragmentInfo,
    LiteralMode,
    Response,
)


class TestFragmentizer(unittest.TestCase):
    def test_enqueue_bytes(self):
        fragmentizer = Fragmentizer(max_message_size=None)
        fragmentizer.enqueue_bytes(b"")
        fragmentizer.enqueue_bytes(b"foo")
        fragmentizer.enqueue_bytes(b"bar")
        fragmentizer.enqueue_bytes(b"\x00")
        fragmentizer.enqueue_bytes(b"\xff")
        fragmentizer.enqueue_bytes(b"\x00foo\xffbar\x00")

    def test_progress(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        info = fragmentizer.progress()
        self.assertEqual(info, None)

        fragmentizer.enqueue_bytes(b"* OK ...\r\n")

        info = fragmentizer.progress()
        self.assertEqual(
            info,
            LineFragmentInfo(
                start=0, end=10, announcement=None, ending=LineEnding.CrLf
            ),
        )

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")

        info = fragmentizer.progress()
        self.assertEqual(
            info,
            LineFragmentInfo(
                start=0,
                end=14,
                announcement=LiteralAnnouncement(LiteralMode.Sync, length=5),
                ending=LineEnding.CrLf,
            ),
        )

        info = fragmentizer.progress()
        self.assertEqual(
            info,
            LiteralFragmentInfo(start=14, end=19),
        )

        info = fragmentizer.progress()
        self.assertEqual(
            info,
            LineFragmentInfo(
                start=19,
                end=25,
                announcement=LiteralAnnouncement(LiteralMode.Sync, length=5),
                ending=LineEnding.CrLf,
            ),
        )

        info = fragmentizer.progress()
        self.assertEqual(info, LiteralFragmentInfo(start=25, end=30))

        info = fragmentizer.progress()
        self.assertEqual(
            info,
            LineFragmentInfo(
                start=30, end=32, announcement=None, ending=LineEnding.CrLf
            ),
        )

        info = fragmentizer.progress()
        self.assertEqual(info, None)

    def test_fragment_bytes(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")

        info = fragmentizer.progress()
        bytes = fragmentizer.fragment_bytes(info)
        self.assertEqual(bytes, b"A1 LOGIN {5}\r\n")

        info = fragmentizer.progress()
        bytes = fragmentizer.fragment_bytes(info)
        self.assertEqual(bytes, b"ABCDE")

        info = fragmentizer.progress()
        bytes = fragmentizer.fragment_bytes(info)
        self.assertEqual(bytes, b" {5}\r\n")

        info = fragmentizer.progress()
        bytes = fragmentizer.fragment_bytes(info)
        self.assertEqual(bytes, b"FGHIJ")

        info = fragmentizer.progress()
        bytes = fragmentizer.fragment_bytes(info)
        self.assertEqual(bytes, b"\r\n")

    def test_is_message_complete(self):
        fragmentizer = Fragmentizer(max_message_size=None)
        self.assertFalse(fragmentizer.is_message_complete())

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")
        self.assertFalse(fragmentizer.is_message_complete())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_message_complete())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_message_complete())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_message_complete())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_message_complete())

        fragmentizer.progress()
        self.assertTrue(fragmentizer.is_message_complete())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_message_complete())

    def test_is_message_poisoned(self):
        fragmentizer = Fragmentizer(max_message_size=None)
        self.assertFalse(fragmentizer.is_message_poisoned())

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")
        self.assertFalse(fragmentizer.is_message_poisoned())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_message_poisoned())

        fragmentizer.poison_message()
        self.assertTrue(fragmentizer.is_message_poisoned())

        fragmentizer.progress()
        self.assertTrue(fragmentizer.is_message_poisoned())

        fragmentizer.progress()
        fragmentizer.progress()
        fragmentizer.progress()
        self.assertTrue(fragmentizer.is_message_poisoned())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_message_poisoned())

    def test_message_bytes(self):
        fragmentizer = Fragmentizer(max_message_size=None)
        bytes = fragmentizer.message_bytes()
        self.assertEqual(bytes, b"")

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")
        bytes = fragmentizer.message_bytes()
        self.assertEqual(bytes, b"")

        fragmentizer.progress()
        bytes = fragmentizer.message_bytes()
        self.assertEqual(bytes, b"A1 LOGIN {5}\r\n")

        fragmentizer.progress()
        bytes = fragmentizer.message_bytes()
        self.assertEqual(bytes, b"A1 LOGIN {5}\r\nABCDE")

        fragmentizer.progress()
        bytes = fragmentizer.message_bytes()
        self.assertEqual(bytes, b"A1 LOGIN {5}\r\nABCDE {5}\r\n")

        fragmentizer.progress()
        bytes = fragmentizer.message_bytes()
        self.assertEqual(bytes, b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ")

        fragmentizer.progress()
        bytes = fragmentizer.message_bytes()
        self.assertEqual(bytes, b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")

    def test_is_max_message_size_exceeded(self):
        fragmentizer = Fragmentizer(max_message_size=20)
        self.assertFalse(fragmentizer.is_max_message_size_exceeded())

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")
        self.assertFalse(fragmentizer.is_max_message_size_exceeded())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_max_message_size_exceeded())

        fragmentizer.progress()
        self.assertFalse(fragmentizer.is_max_message_size_exceeded())

        fragmentizer.progress()
        self.assertTrue(fragmentizer.is_max_message_size_exceeded())

        with self.assertRaises(FragmentizerMessageTooLongError) as cm:
            fragmentizer.decode_command()
        self.assertEqual(
            str(cm.exception),
            "{'initial': b'A1 LOGIN {5}\\r\\nABCDE '}",
        )

    def test_skip_message(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\n* OK ...\r\n")

        info = fragmentizer.progress()
        self.assertEqual(
            info,
            LineFragmentInfo(
                start=0,
                end=14,
                announcement=LiteralAnnouncement(LiteralMode.Sync, length=5),
                ending=LineEnding.CrLf,
            ),
        )

        fragmentizer.skip_message()

        info = fragmentizer.progress()
        self.assertEqual(
            info,
            LineFragmentInfo(
                start=0, end=10, announcement=None, ending=LineEnding.CrLf
            ),
        )

    def test_poison_message(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")

        fragmentizer.progress()
        fragmentizer.poison_message()
        fragmentizer.progress()
        fragmentizer.progress()
        fragmentizer.progress()
        fragmentizer.progress()

        with self.assertRaises(FragmentizerMessagePoisonedError) as cm:
            fragmentizer.decode_command()
        self.assertEqual(
            str(cm.exception),
            "{'discarded': b'A1 LOGIN {5}\\r\\nABCDE {5}\\r\\nFGHIJ\\r\\n'}",
        )

    def test_decode_tag(self):
        fragmentizer = Fragmentizer(max_message_size=None)
        tag = fragmentizer.decode_tag()
        self.assertEqual(tag, None)

        fragmentizer.enqueue_bytes(b"A1 LOGIN {5}\r\nABCDE {5}\r\nFGHIJ\r\n")
        tag = fragmentizer.decode_tag()
        self.assertEqual(tag, None)

        fragmentizer.progress()
        tag = fragmentizer.decode_tag()
        self.assertEqual(tag, "A1")

        fragmentizer.progress()
        fragmentizer.progress()
        fragmentizer.progress()
        fragmentizer.progress()
        tag = fragmentizer.decode_tag()
        self.assertEqual(tag, "A1")

        fragmentizer.progress()
        tag = fragmentizer.decode_tag()
        self.assertEqual(tag, None)

    def test_decode_greeting(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        with self.assertRaises(DecodeIncomplete):
            fragmentizer.decode_greeting()

        fragmentizer.enqueue_bytes(b"* OK ...\r\n")

        fragmentizer.progress()
        greeting = fragmentizer.decode_greeting()
        self.assertEqual(
            greeting, Greeting.from_dict({"kind": "Ok", "code": None, "text": "..."})
        )

        fragmentizer.enqueue_bytes(b"foo\r\n")

        fragmentizer.progress()
        with self.assertRaises(DecodeFailed):
            fragmentizer.decode_greeting()

    def test_decode_command(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        with self.assertRaises(DecodeIncomplete):
            fragmentizer.decode_command()

        fragmentizer.enqueue_bytes(b"A1 NOOP\r\n")

        fragmentizer.progress()
        command = fragmentizer.decode_command()
        self.assertEqual(
            command, Command.from_dict({"tag": "A1", "body": {"type": "Noop"}})
        )

        fragmentizer.enqueue_bytes(b"foo\r\n")

        fragmentizer.progress()
        with self.assertRaises(DecodeFailed):
            fragmentizer.decode_command()

    def test_decode_authenticate_data(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        with self.assertRaises(DecodeIncomplete):
            fragmentizer.decode_authenticate_data()

        fragmentizer.enqueue_bytes(b"dGVzdAB0ZXN0AHRlc3Q=\r\n")

        fragmentizer.progress()
        authenticate_data = fragmentizer.decode_authenticate_data()
        self.assertEqual(
            authenticate_data,
            AuthenticateData.from_dict(
                {"type": "Continue", "content": list(b"test\x00test\x00test")}
            ),
        )

        fragmentizer.enqueue_bytes(b"foo\r\n")

        fragmentizer.progress()
        with self.assertRaises(DecodeFailed):
            fragmentizer.decode_authenticate_data()

    def test_decode_response(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        with self.assertRaises(DecodeIncomplete):
            fragmentizer.decode_response()

        fragmentizer.enqueue_bytes(b"A1 OK ...\r\n")

        fragmentizer.progress()
        response = fragmentizer.decode_response()
        self.assertEqual(
            response,
            Response.from_dict(
                {
                    "type": "Status",
                    "content": {
                        "type": "Tagged",
                        "content": {
                            "tag": "A1",
                            "body": {"kind": "Ok", "code": None, "text": "..."},
                        },
                    },
                }
            ),
        )

        fragmentizer.enqueue_bytes(b"foo\r\n")

        fragmentizer.progress()
        with self.assertRaises(DecodeFailed):
            fragmentizer.decode_response()

    def test_decode_idle_done(self):
        fragmentizer = Fragmentizer(max_message_size=None)

        with self.assertRaises(DecodeIncomplete):
            fragmentizer.decode_idle_done()

        fragmentizer.enqueue_bytes(b"DONE\r\n")

        fragmentizer.progress()
        idle_done = fragmentizer.decode_idle_done()
        self.assertEqual(idle_done, IdleDone())

        fragmentizer.enqueue_bytes(b"foo\r\n")

        fragmentizer.progress()
        with self.assertRaises(DecodeFailed):
            fragmentizer.decode_idle_done()
