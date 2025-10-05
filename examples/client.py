from enum import Enum

from common import read_more, Role
from imap_codec import Fragmentizer, Greeting, Response


WELCOME = """
# Parsing of IMAP greeting and responses

"S:" denotes the server.
".." denotes the continuation of an (incomplete) response, e.g., due to the use of an IMAP literal.

Note: "\\n" will be automatically replaced by "\\r\\n".

--------------------------------------------------------------------------------------------------

Enter intial IMAP greeting followed by IMAP responses (or "exit").

"""


class State(Enum):
    Greeting = 1
    Response = 2


if __name__ == "__main__":
    print(WELCOME)

    fragmentizer = Fragmentizer(max_message_size=10 * 1024)
    state = State.Greeting

    while True:
        res = fragmentizer.progress()

        if not res:
            data = bytes(
                read_more(Role.Server, len(fragmentizer.message_bytes()) != 0), "utf-8"
            )
            fragmentizer.enqueue_bytes(data)
            continue

        if not fragmentizer.is_message_complete():
            continue

        out: Greeting | Response
        if state == State.Greeting:
            try:
                out = fragmentizer.decode_greeting()
                print(out)
                state = State.Response
            except Exception as ex:
                print(f"decode error: {ex}")
        elif state == State.Response:
            try:
                out = fragmentizer.decode_response()
                print(out)
            except Exception as ex:
                print(f"decode error: {ex}")
