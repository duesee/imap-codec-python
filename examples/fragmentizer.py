import sys

from imap_codec import Fragmentizer


def main():
    fragmentizer = Fragmentizer(max_message_size=64)

    while True:
        fragment_info = fragmentizer.progress()
        if fragment_info:
            print(
                f"[!] Fragment: {fragment_info} // {fragmentizer.fragment_bytes(fragment_info)}"
            )
            if fragmentizer.is_message_complete():
                if fragmentizer.is_max_message_size_exceeded():
                    print(
                        f"[!] Message too long, message tag: {repr(fragmentizer.decode_tag())}"
                    )
                else:
                    print(
                        f"[!] Message completed, message bytes: {fragmentizer.message_bytes()}"
                    )
        else:
            print("[!] Reading stdin (ctrl+d to flush)...")
            chunk = sys.stdin.buffer.read(64)
            if not chunk:
                print("[!] Connection closed")
                break
            print(f"[!] Enqueueing {len(chunk)} byte(s) ({chunk})")
            fragmentizer.enqueue_bytes(chunk)


if __name__ == "__main__":
    main()
