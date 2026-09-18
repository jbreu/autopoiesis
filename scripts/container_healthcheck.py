"""Check the Canvas frontend and backend readiness without making a model call."""

import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/canvas", timeout=3) as response:
            content_type = response.headers.get("Content-Type", "")
            if response.status != 200 or "text/html" not in content_type:
                return 1
        request = urllib.request.Request(
            "http://127.0.0.1:8000/ready",
            headers={"X-Session-API-Key": os.environ.get("LOCAL_BACKEND_API_KEY", "")},
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            return 0 if response.status == 200 else 1
    except (OSError, urllib.error.URLError):
        return 1


if __name__ == "__main__":
    sys.exit(main())
