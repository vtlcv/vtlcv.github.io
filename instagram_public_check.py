
#!/usr/bin/env python3
"""Diagnostic-only check of a public Instagram profile page.

No login, cookies, private endpoints, or credentials are used.
This diagnostic does not prove reliable LIVE start/end detection.
"""

import re
import sys
import urllib.error
import urllib.parse
import urllib.request


def main():
    username = (
        sys.argv[1] if len(sys.argv) > 1 else "eatdrinkplayshare"
    ).strip().lstrip("@").strip("/")

    if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", username):
        print("INVALID_USERNAME")
        return 2

    url = f"https://www.instagram.com/{username}/"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = response.status
            final_url = response.geturl()
            body = response.read(2_000_000)

    except urllib.error.HTTPError as exc:
        print(f"HTTP_STATUS={exc.code}")
        print("RESULT=BLOCKED_OR_UNAVAILABLE")
        return 0

    except Exception as exc:
        print(f"REQUEST_ERROR={type(exc).__name__}: {exc}")
        print("RESULT=REQUEST_FAILED")
        return 0

    html = body.decode("utf-8", errors="replace")
    lower = html.lower()

    print(f"USERNAME={username}")
    print(f"HTTP_STATUS={status}")
    print(f"FINAL_HOST={urllib.parse.urlparse(final_url).netloc}")
    print(f"HTML_BYTES={len(body)}")

    login_wall = (
        "accounts/login" in lower
        or "login required" in lower
    )

    print(f"LOGIN_WALL={login_wall}")

    markers = (
        '"is_live":true',
        '"islive":true',
        '"broadcast_status":"live"',
        '"media_type":"broadcast"',
    )

    found = [marker for marker in markers if marker in lower]

    print(
        "LIVE_MARKERS="
        + (",".join(found) if found else "none")
    )

    if login_wall or len(body) < 1000:
        print("RESULT=PAGE_NOT_USABLE_FOR_PUBLIC_LIVE_CHECK")
    elif found:
        print("RESULT=POSSIBLE_MARKERS_NOT_YET_VALIDATED")
    else:
        print("RESULT=PAGE_REACHABLE_NO_VERIFIABLE_LIVE_SIGNAL")

    print(
        "NOTE=Page access or marker presence alone does not "
        "validate LIVE start/end detection."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
