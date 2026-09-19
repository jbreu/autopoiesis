#!/usr/bin/env python3
"""Select or create the isolated Git branch used for an Autopoiesis task."""

from argparse import ArgumentParser  # noqa: I001
from os import environ
from pathlib import Path
from re import sub
from subprocess import CompletedProcess, run


PROTECTED_BRANCHES = {"main", "master"}
TASK_BRANCH_PREFIXES = ("ai/", "openhands/")


class TaskBranchError(RuntimeError):
    """Raised when a safe task branch cannot be prepared."""


def run_git(path: Path, *args: str) -> CompletedProcess[str]:
    return run(
        ["git", "-C", str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def git(path: Path, *args: str) -> str:
    result = run_git(path, *args)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise TaskBranchError(message)
    return result.stdout.strip()


def repo_info(path: Path) -> tuple[Path, Path] | None:
    top_result = run_git(path, "rev-parse", "--show-toplevel")
    if top_result.returncode != 0:
        return None
    top = Path(top_result.stdout.strip()).resolve()
    common = Path(git(path, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = top / common
    return top, common.resolve()


def normalize_slug(value: str) -> str:
    slug = sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise TaskBranchError("Task name must contain at least one letter or digit.")
    return slug[:60].rstrip("-")


def current_branch(repo: Path) -> str:
    branch = git(repo, "branch", "--show-current")
    if not branch:
        raise TaskBranchError("Detached HEAD is not a safe task workspace.")
    return branch


def ensure_clean(repo: Path) -> None:
    if git(repo, "status", "--porcelain"):
        raise TaskBranchError(
            f"Working tree {repo} has uncommitted changes; preserve or resolve them first."
        )


def prepare_task_branch(
    repo_root: Path, working_dir: Path, task_name: str
) -> tuple[Path, str, bool]:
    canonical = repo_info(repo_root)
    if canonical is None:
        raise TaskBranchError(f"{repo_root} is not a Git repository.")
    canonical_top, canonical_common = canonical

    active = repo_info(working_dir)
    target = active[0] if active is not None and active[1] == canonical_common else canonical_top
    linked_worktree = target != canonical_top

    branch = current_branch(target)
    desired_branch = f"ai/{normalize_slug(task_name)}"

    if linked_worktree and branch not in PROTECTED_BRANCHES:
        return target, branch, False
    if branch == desired_branch:
        return target, branch, False
    if branch.startswith(TASK_BRANCH_PREFIXES):
        raise TaskBranchError(
            f"Canonical checkout is already assigned to task branch {branch}; "
            "finish that task or return it to its base branch first."
        )

    ensure_clean(target)
    branch = desired_branch
    branch_ref = run_git(
        target, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"
    )
    if branch_ref.returncode == 0:
        raise TaskBranchError(f"Branch {branch} already exists; choose a unique task name.")

    git(target, "switch", "-c", branch)
    return target, branch, True


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("task_name", help="Short name used if an ai/* branch must be created")
    args = parser.parse_args()

    repo_root = Path(environ.get("AUTOPOIESIS_REPO_ROOT", "/projects/app")).resolve()
    working_dir = Path.cwd().resolve()
    try:
        target, branch, created = prepare_task_branch(repo_root, working_dir, args.task_name)
    except TaskBranchError as exc:
        parser.exit(2, f"autopoiesis: {exc}\n")

    print(f"AUTOPOIESIS_TASK_ROOT={target}")
    print(f"AUTOPOIESIS_TASK_BRANCH={branch}")
    print(f"AUTOPOIESIS_TASK_BRANCH_ACTION={'created' if created else 'reusing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
