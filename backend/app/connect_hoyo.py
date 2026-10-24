"""Connect via SSH/stdin, never via the public HTTP API or command-line secrets."""
import asyncio
import json
import sys

from app.services.hoyo import HoyoAPIError
from app.services.hoyo_session import connect, load_sessions, save_sessions


async def main():
    if len(sys.argv) == 3 and sys.argv[1] == "disconnect":
        sessions = load_sessions()
        sessions.pop(sys.argv[2], None)
        save_sessions(sessions)
        print("HoYoverse connection removed for UID " + sys.argv[2])
        return
    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536:
        raise HoyoAPIError("Input is too large.")
    try:
        cookies = json.loads(raw)
        if not isinstance(cookies, dict):
            raise ValueError()
    except ValueError:
        raise HoyoAPIError("Expected cookie JSON on stdin.") from None
    for role in await connect(cookies):
        print(f"Connected UID {role['uid']} ({role['region']})")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except HoyoAPIError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Could not save HoYoverse connection. Check server storage permissions.", file=sys.stderr)
        sys.exit(1)
