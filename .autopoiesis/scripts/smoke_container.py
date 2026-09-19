"""Verify the running container mounts the repository and keeps data in its harness."""

import os
import subprocess
import tempfile
from pathlib import Path

root = Path("/projects/app")
harness = root / ".autopoiesis"
assert (root / "AGENTS.md").is_file()
assert (harness / "AGENTS.md").is_file()
assert (root / "src/repo_demo").is_dir()
assert os.access(root, os.W_OK)

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

print("Full Git repository, agent instructions, state, temporary files, and cache verified.")
