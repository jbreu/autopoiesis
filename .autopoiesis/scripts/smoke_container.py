"""Verify the running container mounts the repository and keeps data in its harness."""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from openhands.sdk.context import AgentContext
from openhands.sdk.skills import load_user_skills

root = Path("/projects/app")
harness = root / ".autopoiesis"
assert (root / "AGENTS.md").is_file()
assert (harness / "AGENTS.md").is_file()
assert (root / "src/repo_demo").is_dir()
assert os.access(root, os.W_OK)

# A fresh chat may have no project context because Canvas starts it in scratch.
# Check user-skill discovery and full prompt inclusion without model inference.
context_name = "autopoiesis-repository"
context_file = Path.home() / f".openhands/skills/{context_name}.md"
assert context_file.read_bytes() == (harness / f"config/{context_name}.md").read_bytes()
assert os.statvfs(context_file).f_flag & os.ST_RDONLY, "Repository context must be read-only"
skills = [skill for skill in load_user_skills() if skill.name == context_name]
assert len(skills) == 1, "Repository context was not discovered as a user skill"
assert skills[0].get_skill_type() == "repo", "Context must load without a keyword trigger"
context = AgentContext(skills=skills, current_datetime=None)
for prompt in (context.get_system_message_suffix(), context.to_acp_prompt_context()):
    assert "/projects/app/AGENTS.md" in prompt
    assert "/projects/app/.autopoiesis/AGENTS.md" in prompt

# Verify the running backend too; it can use a different SDK than python3.
request = Request(
    "http://127.0.0.1:8000/api/skills",
    data=json.dumps(
        {"load_public": False, "load_user": True, "load_project": False, "load_org": False}
    ).encode(),
    headers={
        "X-Session-API-Key": os.environ["LOCAL_BACKEND_API_KEY"],
        "Content-Type": "application/json",
    },
    method="POST",
)
with urlopen(request, timeout=30) as response:
    catalog = json.load(response)
assert any(
    skill["name"] == context_name and skill["type"] == "repo" for skill in catalog["skills"]
), "The running backend did not discover always-loaded repository context"

git_root = subprocess.run(
    ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
    check=True,
    capture_output=True,
    text=True,
    timeout=10,
).stdout.strip()
assert Path(git_root).resolve() == root

tracked = set(
    subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout.splitlines()
)
assert {"AGENTS.md", ".autopoiesis/AGENTS.md", "src/repo_demo/__init__.py"} <= tracked

for mounted, local in (
    (Path.home() / ".openhands", harness / "state"),
    (Path(os.environ["XDG_CACHE_HOME"]), harness / "cache"),
    (Path(tempfile.gettempdir()), harness / "tmp"),
):
    with tempfile.NamedTemporaryFile(dir=mounted) as probe:
        probe.write(b"harness mount probe")
        probe.flush()
        assert (local / Path(probe.name).name).read_bytes() == b"harness mount probe"

with tempfile.TemporaryDirectory() as directory:
    scratch = Path(directory)
    source = scratch / "probe.py"
    source.write_text("value = 1\n")
    subprocess.run(
        [
            os.environ["PROJECT_PYTHON"],
            "-m",
            "ruff",
            "check",
            "--config",
            str(harness / "ruff.toml"),
            ".",
        ],
        cwd=scratch,
        check=True,
        capture_output=True,
        timeout=10,
    )
    assert list(scratch.iterdir()) == [source], "Ruff left cache files in the working directory"
    assert Path(os.environ["RUFF_CACHE_DIR"]) == harness / "cache/ruff"
    assert (harness / "cache/ruff").is_dir()

print(
    "Full Git repository, automatic OpenHands/ACP context, agent instructions, "
    "state, temporary files, and cache verified."
)
