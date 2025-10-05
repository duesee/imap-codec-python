from dataclasses import dataclass
from typing import TypeAlias

from common import COLOR_SERVER, read_more, RESET, Role
from imap_codec import (
    AuthenticateData,
    Command,
    Fragmentizer,
    IdleDone,
    LineFragmentInfo,
)


WELCOME = """
# Parsing of IMAP commands

"C:" denotes the client,
"S:" denotes the server, and
".." denotes the continuation of an (incomplete) command, e.g., due to the use of an IMAP literal.

Note: "\\n" will be automatically replaced by "\\r\\n".

--------------------------------------------------------------------------------------------------

Enter IMAP commands (or "exit").

"""


@dataclass
class StateCommand:
    pass


@dataclass
class StateAuthenticate:
    tag: str


@dataclass
class StateIdle:
    pass


State: TypeAlias = StateCommand | StateAuthenticate | StateIdle


if __name__ == "__main__":
    print(WELCOME)

    fragmentizer = Fragmentizer(max_message_size=10 * 1024)
    state: State = StateCommand()

    print(f"S: {COLOR_SERVER}* OK ...{RESET}")

    while True:
        res = fragmentizer.progress()

        if not res:
            data = bytes(
                read_more(Role.Client, len(fragmentizer.message_bytes()) != 0), "utf-8"
            )
            fragmentizer.enqueue_bytes(data)
            continue

        if isinstance(res, LineFragmentInfo):
            if res.announcement:
                length = res.announcement.length
                mode = res.announcement.mode
                if length <= 1024:
                    print(f"S: {COLOR_SERVER}+ {RESET}")
                    continue
                else:
                    tag = fragmentizer.decode_tag()
                    if tag:
                        print(f"S: {COLOR_SERVER}{tag} BAD ...{RESET}")
                        fragmentizer.skip_message()
                        continue
                    else:
                        fragmentizer.poison_message()
                        continue

        if not fragmentizer.is_message_complete():
            continue

        out: Command | AuthenticateData | IdleDone

        if isinstance(state, StateCommand):
            try:
                out = fragmentizer.decode_command()
                print(out)
                if "Authenticate" in out.as_dict()["body"]:
                    # Request another SASL round ...
                    print(f"S: {COLOR_SERVER}+ {RESET}")
                    # ... and proceed with authenticate data.
                    state = StateAuthenticate(tag=out.as_dict()["tag"])
                elif out.as_dict()["body"] == "Idle":
                    # Accept the idle ...
                    print(f"S: {COLOR_SERVER}+ ...{RESET}")
                    # ... and proceed with idle done.
                    state = StateIdle()
                else:
                    pass
            except Exception as ex:
                print(f"decode error: {ex}")
        elif isinstance(state, StateAuthenticate):
            try:
                out = fragmentizer.decode_authenticate_data()
                print(out)
                # Accept the authentication after one SASL round ...
                print(f"S: {COLOR_SERVER}{state.tag} OK ...{RESET}")
                # ... and proceed with commands.
                state = StateCommand()
            except Exception as ex:
                print(f"decode error: {ex}")
        elif isinstance(state, StateIdle):
            try:
                out = fragmentizer.decode_idle_done()
                print(out)
                # End idle and proceed with commands.
                state = StateCommand()
            except Exception as ex:
                print(f"decode error: {ex}")
