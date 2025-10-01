from __future__ import annotations

from typing import Optional, Tuple, Union

class DecodeError(Exception):
    """
    Error during decoding.
    """

class DecodeFailed(DecodeError):
    """
    "Failed" error during decoding:
    Decoding failed.
    """

class DecodeIncomplete(DecodeError):
    """
    "Incomplete" error during decoding:
    More data is needed.
    """

class DecodeLiteralFound(DecodeError):
    """
    "LiteralFound" error during decoding:
    The decoder stopped at the beginning of literal data.
    """

class LiteralMode:
    """
    Literal mode, i.e., sync or non-sync.

    - Sync: A synchronizing literal, i.e., `{<n>}\r\n<data>`.
    - NonSync: A non-synchronizing literal according to RFC 7888, i.e., `{<n>+}\r\n<data>`.

    Warning: The non-sync literal extension must only be used when the server advertised support
             for it sending the LITERAL+ or LITERAL- capability.
    """

    Sync: LiteralMode
    NonSync: LiteralMode

class LineFragment:
    """
    Fragment of a line that is ready to be send.
    """

    def __init__(self, data: bytes) -> None:
        """
        Create a line fragment from data bytes

        :param data: Data bytes of fragment
        :raises TypeError: `data` is not byte-like
        """

    @property
    def data(self) -> bytes:
        """
        Get line fragment data bytes

        :return: Data bytes of fragment
        """

class LiteralFragment:
    """
    Fragment of a literal that may require an action before it should be send.
    """

    def __init__(self, data: bytes, mode: LiteralMode) -> None:
        """
        Create a literal fragment from data bytes and literal mode

        :param data: Data bytes of fragment
        :param mode: Literal mode
        :raises TypeError: `data` is not byte-like
        :raises TypeError: `mode` is invalid
        """

    @property
    def data(self) -> bytes:
        """
        Get literal fragment data bytes

        :return: Data bytes of fragment
        """

    @property
    def mode(self) -> LiteralMode:
        """
        Get literal fragment literal mode

        :return: Literal mode
        """

class Encoded:
    """
    An encoded message.

    This struct facilitates the implementation of IMAP client- and server implementations by
    yielding the encoding of a message through fragments. This is required, because the usage of
    literals (and some other types) may change the IMAP message flow. Thus, in many cases, it is an
    error to just "dump" a message and send it over the network.
    """

    def __iter__(self) -> Encoded: ...
    def __next__(self) -> Union[LineFragment, LiteralFragment]: ...
    def dump(self) -> bytes:
        """
        Dump the (remaining) encoded data without being guided by fragments.
        """

class Greeting:
    """
    Greeting.

    Note: Don't use `code: None` *and* a `text` that starts with "[" as this would be ambiguous in IMAP.
    We could fix this but the fix would make this type unconformable to use.
    """

    @staticmethod
    def from_dict(greeting: dict) -> Greeting:
        """
        Create greeting from `dict`

        :param greeting: Dictionary representation of greeting
        :raises RuntimeError: Dictionary could not be deserialized into greeting
        """

    def as_dict(self) -> dict:
        """
        Return greeting as `dict`

        :return: Dictionary representation of greeting
        """

class GreetingCodec:
    """
    Codec for greetings.
    """

    @staticmethod
    def decode(bytes: bytes) -> Tuple[bytes, Greeting]:
        """
        Decode greeting from given bytes.

        :param bytes: Given bytes
        :raises DecodeFailed: Decoding failed.
        :raises DecodeIncomplete: More data is needed.
        :return: Tuple of remaining bytes and decoded greeting
        """

    @staticmethod
    def encode(greeting: Greeting) -> Encoded:
        """
        Encode greeting into fragments.

        :param greeting: Given greeting
        :return: `Encoded` type holding fragments of encoded greeting
        """

class Command:
    """
    Command.
    """

    @staticmethod
    def from_dict(command: dict) -> Command:
        """
        Create command from `dict`

        :param command: Dictionary representation of command
        :raises RuntimeError: Dictionary could not be deserialized into command
        """

    def as_dict(self) -> dict:
        """
        Return command as `dict`

        :return: Dictionary representation of command
        """

class CommandCodec:
    """
    Codec for commands.
    """

    @staticmethod
    def decode(bytes: bytes) -> Tuple[bytes, Command]:
        """
        Decode command from given bytes.

        :param bytes: Given bytes
        :raises DecodeFailed: Decoding failed.
        :raises DecodeIncomplete: More data is needed.
        :raises DecodeLiteralFound: The decoder stopped at the beginning of literal data.
        :return: Tuple of remaining bytes and decoded command
        """

    @staticmethod
    def encode(command: Command) -> Encoded:
        """
        Encode command into fragments.

        :param command: Given command
        :return: `Encoded` type holding fragments of encoded command
        """

class AuthenticateData:
    """
    Authenticate data line

    Data line used, e.g., during AUTHENTICATE.
    """

    @staticmethod
    def from_dict(authenticate_data: dict) -> AuthenticateData:
        """
        Create authenticate data line from `dict`

        :param authenticate_data: Dictionary representation of authenticate data line
        :raises RuntimeError: Dictionary could not be deserialized into authenticate data line
        """

    def as_dict(self) -> dict:
        """
        Return authenticate data line as `dict`

        :return: Dictionary representation of authenticate data line
        """

class AuthenticateDataCodec:
    """
    Codec for authenticate data lines.
    """

    @staticmethod
    def decode(bytes: bytes) -> Tuple[bytes, AuthenticateData]:
        """
        Decode authenticate data line from given bytes.

        :param bytes: Given bytes
        :raises DecodeFailed: Decoding failed.
        :raises DecodeIncomplete: More data is needed.
        :return: Tuple of remaining bytes and decoded authenticate data line
        """

    @staticmethod
    def encode(authenticate_data: AuthenticateData) -> Encoded:
        """
        Encode authenticate data line into fragments.

        :param authenticate_data: Given authenticate data line
        :return: `Encoded` type holding fragments of encoded authenticate data line
        """

class Response:
    """
    Response.
    """

    @staticmethod
    def from_dict(response: dict) -> Response:
        """
        Create response from `dict`

        :param response: Dictionary representation of response
        :raises RuntimeError: Dictionary could not be deserialized into response
        """

    def as_dict(self) -> dict:
        """
        Return response as `dict`

        :return: Dictionary representation of response
        """

class ResponseCodec:
    """
    Codec for responses.
    """

    @staticmethod
    def decode(bytes: bytes) -> Tuple[bytes, Response]:
        """
        Decode response from given bytes.

        :param bytes: Given bytes
        :raises DecodeFailed: Decoding failed.
        :raises DecodeIncomplete: More data is needed.
        :raises DecodeLiteralFound: The decoder stopped at the beginning of literal data.
        :return: Tuple of remaining bytes and decoded response
        """

    @staticmethod
    def encode(response: Response) -> Encoded:
        """
        Encode response into fragments.

        :param response: Given response
        :return: `Encoded` type holding fragments of encoded response
        """

class IdleDone:
    """
    Denotes the continuation data message "DONE\r\n" to end the IDLE command.
    """

    def __new__(cls) -> IdleDone:
        """
        Create idle done
        """

class IdleDoneCodec:
    """
    Codec for idle dones.
    """

    @staticmethod
    def decode(bytes: bytes) -> Tuple[bytes, IdleDone]:
        """
        Decode idle done from given bytes.

        :param bytes: Given bytes
        :raises DecodeFailed: Decoding failed.
        :raises DecodeIncomplete: More data is needed.
        :raises DecodeLiteralFound: The decoder stopped at the beginning of literal data.
        :return: Tuple of remaining bytes and decoded idle done
        """

    @staticmethod
    def encode(idle_done: IdleDone) -> Encoded:
        """
        Encode idle done into fragments.

        :param idle_done: Given idle done
        :return: `Encoded` type holding fragments of encoded idle done
        """

class LineEnding:
    """
    The character sequence used for ending a line.

    - Lf: The line ends with the character `\n`.
    - CrLf: The line ends with the character sequence `\r\n`.
    """

    Lf: LineEnding
    CrLf: LineEnding

class LiteralAnnouncement:
    """
    When the `Fragmentizer` finds a line this is used to announce a literal following the line
    """

    def __init__(self, mode: LiteralMode, length: int) -> None:
        """
        Create a literal announcement from literal mode and a byte length

        :param mode: Literal mode of the announced literal
        :param length: Length of the announced literal in bytes
        :raises TypeError: `mode` is invalid
        :raises TypeError: `length` is not interger-like
        """

    @property
    def mode(self) -> LiteralMode:
        """
        Get the literal mode of the announced literal

        :return: Literal mode
        """

    @property
    def length(self) -> int:
        """
        Get the length of the announced literal in bytes

        :return: Length in bytes
        """

class LineFragmentInfo:
    """
    Describes a literal fragment of the current message found by `Fragmentizer.progress`.

    The corresponding bytes can be retrieved via `Fragmentizer.fragment_bytes` until `Fragmentizer.is_message_complete`
    returns true. After that the next call of `Fragmentizer.progress` will start the next message.
    """

    def __init__(
        self,
        start: int,
        end: int,
        announcement: Optional[LiteralAnnouncement],
        ending: LineEnding,
    ) -> None:
        """
        Create a line fragment info from start and end index, literal announcement and line ending

        :param start: Inclusive start index relative to the current message
        :param length: Exclusive end index relative to the current message
        :param announcement: Whether the next fragment will be a literal
        :param ending: The detected ending sequence for this line
        :raises TypeError: `start` is not interger-like
        :raises TypeError: `end` is not interger-like
        :raises TypeError: `announcement` is invalid
        :raises TypeError: `ending` is invalid
        """

    @property
    def start(self) -> int:
        """
        Get the start index of the line fragment

        :return: Inclusive start index relative to the current message
        """

    @property
    def end(self) -> int:
        """
        Get the end index of the line fragment

        :return: Exclusive end index relative to the current message
        """

    @property
    def announcement(self) -> Optional[LiteralAnnouncement]:
        """
        Get the literal announcement of the line fragment

        :return: Whether the next fragment will be a literal
        """

    @property
    def ending(self) -> LineEnding:
        """
        Get the line ending of the line fragment

        :return: The detected ending sequence for this line
        """

class LiteralFragmentInfo:
    """
    Describes a literal fragment of the current message found by `Fragmentizer.progress`

    The corresponding bytes can be retrieved via `Fragmentizer.fragment_bytes` until `Fragmentizer.is_message_complete`
    returns true. After that the next call of `Fragmentizer.progress` will start the next message.
    """

    def __init__(self, start: int, end: int) -> None:
        """
        Create a literal fragment info from start and end index

        :param start: Inclusive start index relative to the current message
        :param length: Exclusive end index relative to the current message
        :raises TypeError: `start` is not interger-like
        :raises TypeError: `end` is not interger-like
        """

    @property
    def start(self) -> int:
        """
        Get the start index of the literal fragment

        :return: Inclusive start index relative to the current message
        """

    @property
    def end(self) -> int:
        """
        Get the end index of the literal fragment

        :return: Exclusive end index relative to the current message
        """

class FragmentizerDecodeError(Exception):
    """
    The decoder failed decoding the message.
    """

class FragmentizerDecodingRemainderError(FragmentizerDecodeError):
    """
    Not all bytes of the message were used when decoding the message.
    """

class FragmentizerMessageTooLongError(FragmentizerDecodeError):
    """
    Max message size was exceeded and bytes were dropped.
    """

class FragmentizerMessagePoisonedError(FragmentizerDecodeError):
    """
    The message was explicitly poisoned to prevent decoding.
    """

class Fragmentizer:
    """
    Safely splits IMAP bytes into line and literal fragments.
    """

    def __init__(self, max_message_size: Optional[int]) -> None:
        """
        Create `Fragmentizer` with maximum message size.
        """

    def progress(self) -> Optional[Union[LineFragmentInfo, LiteralFragmentInfo]]:
        """
        Continue parsing current message until next fragment is detected.
        """

    def enqueue_bytes(self, data: bytes) -> None:
        """
        Enqueues more bytes.
        """

    def fragment_bytes(
        self, fragment_info: Union[LineFragmentInfo, LiteralFragmentInfo]
    ) -> bytes:
        """
        Return bytes for fragment of current message.
        """

    def is_message_complete(self) -> bool:
        """
        Return whether current message was fully parsed.
        """

    def is_message_poisoned(self) -> bool:
        """
        Return whether current message was explicitly poisoned to prevent decoding.
        """

    def message_bytes(self) -> bytes:
        """
        Return bytes of current message.
        """

    def is_max_message_size_exceeded(self) -> bool:
        """
        Return whether size limit is exceeded for current message.
        """

    def skip_message(self) -> None:
        """
        Skip current message and start next message immediately.

        Warning: This method might be dangerous. If client and server don't
        agree at which point a message is skipped, then the client or server might
        treat untrusted bytes (e.g. literal bytes) as IMAP messages. Currently the
        only valid use-case is a server that rejects synchronizing literals from the
        client. Otherwise consider using `poison_message`.
        """

    def poison_message(self) -> None:
        """
        Poison current message to prevent its decoding.
        """

    def decode_tag(self) -> Optional[str]:
        """
        Try to decode tag for current message.
        """

    def decode_greeting(self) -> Greeting:
        """
        Try to decode current message as "greeting".
        """

    def decode_command(self) -> Command:
        """
        Try to decode current message as "command".
        """

    def decode_authenticate_data(self) -> AuthenticateData:
        """
        Try to decode current message as "authenticate data".
        """

    def decode_response(self) -> Response:
        """
        Try to decode current message as "response".
        """

    def decode_idle_done(self) -> IdleDone:
        """
        Try to decode current message as "idle done".
        """
