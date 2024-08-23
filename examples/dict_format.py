from imap_codec import Greeting, GreetingCodec

buffer = b"* OK Hello, World!\r\n<remaining>"

# Decode buffer into a greeting
remaining, greeting = GreetingCodec.decode(buffer)
assert remaining == b"<remaining>"
assert isinstance(greeting, Greeting)

# Extract greeting data as dictionary
data = greeting.as_dict()
assert data["kind"] == {"type": "Ok"}
assert data["code"] is None
assert data["text"] == "Hello, World!"

# Extract more complex dictionary
buffer = b"* OK [PERMANENTFLAGS (\\* \\Seen we)] (Success)\r\n"
_, greeting = GreetingCodec.decode(buffer)
data = greeting.as_dict()
assert data["kind"] == {"type": "Ok"}
assert data["code"] == {
    "type": "PermanentFlags",
    "data": [
        {"type": "Asterisk"},
        {"type": "Flag", "data": {"type": "Seen"}},
        {"type": "Flag", "data": {"type": "Keyword", "data": "we"}},
    ],
}
assert data["text"] == "(Success)"
