"""Create local configuration once, without printing credentials."""

import os
import secrets
from pathlib import Path


def initialize(root: Path) -> bool:
    for directory in ("state", "state/skills", "tmp", "cache"):
        (root / directory).mkdir(mode=0o700, exist_ok=True)
    template = (root / ".env.example").read_text(encoding="utf-8")
    template = template.replace(
        "LOCAL_BACKEND_API_KEY=change-me", "LOCAL_BACKEND_API_KEY=" + secrets.token_hex(32)
    )
    template = template.replace("OH_SECRET_KEY=change-me", "OH_SECRET_KEY=" + secrets.token_hex(32))
    if hasattr(os, "getuid") and os.getuid() > 0 and os.getgid() > 0:
        template = template.replace("AGENT_UID=1000", f"AGENT_UID={os.getuid()}")
        template = template.replace("AGENT_GID=1000", f"AGENT_GID={os.getgid()}")
    try:
        fd = os.open(root / ".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        output.write(template)
    return True


if __name__ == "__main__":
    created = initialize(Path(__file__).resolve().parents[1])
    print(
        "Created .autopoiesis/.env with local secrets."
        if created
        else ".autopoiesis/.env already exists; left unchanged."
    )
