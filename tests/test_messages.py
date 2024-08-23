import unittest

from imap_codec import AuthenticateData, Command, Greeting, IdleDone, Response


class TestGreeting(unittest.TestCase):
    def test_from_dict(self):
        self.assertIsInstance(
            Greeting.from_dict(
                {
                    "code": {"type": "Alert"},
                    "kind": {"type": "Ok"},
                    "text": "Hello, World!",
                }
            ),
            Greeting,
        )

        self.assertIsInstance(
            Greeting.from_dict(
                {"code": None, "kind": {"type": "Ok"}, "text": "Hello, World!"}
            ),
            Greeting,
        )

        with self.assertRaises(RuntimeError) as cm:
            Greeting.from_dict({"text": "Hello, World!"})
        self.assertEqual(str(cm.exception), "missing field `kind`")

    def test_as_dict(self):
        dictionary = {
            "code": {"type": "Alert"},
            "kind": {"type": "Ok"},
            "text": "Hello, World!",
        }
        self.assertEqual(Greeting.from_dict(dictionary).as_dict(), dictionary)

        dictionary = {"code": None, "kind": {"type": "Ok"}, "text": "Hello, World!"}
        self.assertEqual(Greeting.from_dict(dictionary).as_dict(), dictionary)

        self.assertEqual(
            Greeting.from_dict(
                {"kind": {"type": "Ok"}, "text": "Hello, World!"}
            ).as_dict(),
            {"code": None, "kind": {"type": "Ok"}, "text": "Hello, World!"},
        )

    def test_repr(self):
        self.assertEqual(
            repr(
                Greeting.from_dict(
                    {
                        "code": {"type": "Alert"},
                        "kind": {"type": "Ok"},
                        "text": "Hello, World!",
                    }
                )
            ),
            r"Greeting({'kind': {'type': 'Ok'}, 'code': {'type': 'Alert'}, 'text': 'Hello, World!'})",
        )

        self.assertEqual(
            repr(Greeting.from_dict({"kind": {"type": "Ok"}, "text": "Hello, World!"})),
            r"Greeting({'kind': {'type': 'Ok'}, 'code': None, 'text': 'Hello, World!'})",
        )


class TestCommand(unittest.TestCase):
    def test_from_dict(self):
        self.assertIsInstance(
            Command.from_dict({"tag": "a", "body": {"type": "Noop"}}),
            Command,
        )

        with self.assertRaises(RuntimeError) as cm:
            Command.from_dict({"body": {"type": "Noop"}})
        self.assertEqual(str(cm.exception), "missing field `tag`")

    def test_as_dict(self):
        dictionary = {"tag": "a", "body": {"type": "Noop"}}
        self.assertEqual(Command.from_dict(dictionary).as_dict(), dictionary)

    def test_repr(self):
        self.assertEqual(
            repr(Command.from_dict({"tag": "a", "body": {"type": "Noop"}})),
            r"Command({'tag': 'a', 'body': {'type': 'Noop'}})",
        )


class TestAuthenticateData(unittest.TestCase):
    def test_from_dict(self):
        self.assertIsInstance(
            AuthenticateData.from_dict({"type": "Continue", "data": list(b"Test")}),
            AuthenticateData,
        )
        self.assertIsInstance(
            AuthenticateData.from_dict({"type": "Cancel"}),
            AuthenticateData,
        )

    def test_as_dict(self):
        dictionary = {"type": "Continue", "data": list(b"Test")}
        self.assertEqual(AuthenticateData.from_dict(dictionary).as_dict(), dictionary)

        dictionary = {"type": "Cancel"}
        self.assertEqual(AuthenticateData.from_dict(dictionary).as_dict(), dictionary)

    def test_repr(self):
        self.assertEqual(
            repr(
                AuthenticateData.from_dict({"type": "Continue", "data": list(b"Test")})
            ),
            r"AuthenticateData({'type': 'Continue', 'data': [84, 101, 115, 116]})",
        )

        self.assertEqual(
            repr(AuthenticateData.from_dict({"type": "Cancel"})),
            r"AuthenticateData({'type': 'Cancel'})",
        )


class TestResponse(unittest.TestCase):
    def test_from_dict(self):
        self.assertIsInstance(
            Response.from_dict(
                {"type": "Data", "data": {"type": "Search", "data": [1]}}
            ),
            Response,
        )

    def test_as_dict(self):
        dictionary = {"type": "Data", "data": {"type": "Search", "data": [1]}}
        self.assertEqual(Response.from_dict(dictionary).as_dict(), dictionary)

    def test_repr(self):
        self.assertEqual(
            repr(
                Response.from_dict(
                    {"type": "Data", "data": {"type": "Search", "data": [1]}}
                )
            ),
            r"Response({'type': 'Data', 'data': {'type': 'Search', 'data': [1]}})",
        )


class TestIdleDone(unittest.TestCase):
    def test_new(self):
        self.assertIsInstance(
            IdleDone(),
            IdleDone,
        )

    def test_repr(self):
        self.assertEqual(
            repr(IdleDone()),
            "IdleDone",
        )
