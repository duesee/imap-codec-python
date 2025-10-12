import unittest

from imap_codec import (
    Encoded,
    LineFragment,
    LiteralFragment,
    LiteralMode,
    Response,
    ResponseCodec,
)


class TestResponseEncode(unittest.TestCase):
    def test_simple_response(self):
        response = Response.from_dict(
            {"type": "Data", "content": {"type": "Search", "content": [1]}}
        )
        encoded = ResponseCodec.encode(response)
        self.assertIsInstance(encoded, Encoded)
        fragments = list(encoded)
        self.assertEqual(fragments, [LineFragment(b"* SEARCH 1\r\n")])

    def test_simple_response_dump(self):
        response = Response.from_dict(
            {"type": "Data", "content": {"type": "Search", "content": [1]}}
        )
        encoded = ResponseCodec.encode(response)
        self.assertIsInstance(encoded, Encoded)
        self.assertEqual(encoded.dump(), b"* SEARCH 1\r\n")

    _MULTI_FRAGMENT_RESPONSE = Response.from_dict(
        {
            "type": "Data",
            "content": {
                "type": "Fetch",
                "content": {
                    "seq": 12345,
                    "items": [
                        {
                            "type": "BodyExt",
                            "content": {
                                "section": None,
                                "origin": None,
                                "data": {
                                    "type": "Literal",
                                    "content": {
                                        "data": list(b"ABCDE"),
                                        "mode": "NonSync",
                                    },
                                },
                            },
                        }
                    ],
                },
            },
        }
    )

    def test_multi_fragment_response(self):
        encoded = ResponseCodec.encode(self._MULTI_FRAGMENT_RESPONSE)
        self.assertIsInstance(encoded, Encoded)
        fragments = list(encoded)
        self.assertEqual(
            fragments,
            [
                LineFragment(b"* 12345 FETCH (BODY[] {5+}\r\n"),
                LiteralFragment(b"ABCDE", LiteralMode.NonSync),
                LineFragment(b")\r\n"),
            ],
        )

    def test_multi_fragment_response_dump(self):
        encoded = ResponseCodec.encode(self._MULTI_FRAGMENT_RESPONSE)
        self.assertIsInstance(encoded, Encoded)
        self.assertEqual(
            encoded.dump(),
            b"* 12345 FETCH (BODY[] {5+}\r\nABCDE)\r\n",
        )

    def test_multi_fragment_response_dump_remaining(self):
        encoded = ResponseCodec.encode(self._MULTI_FRAGMENT_RESPONSE)
        self.assertIsInstance(encoded, Encoded)
        self.assertEqual(next(encoded), LineFragment(b"* 12345 FETCH (BODY[] {5+}\r\n"))
        self.assertEqual(
            encoded.dump(),
            b"ABCDE)\r\n",
        )
