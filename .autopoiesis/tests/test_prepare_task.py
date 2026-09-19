"""Verify safe task branch selection for Autopoiesis frontend tasks."""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prepare_task", HARNESS / "scripts" / "prepare_task.py"
)
prepare_task = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare_task)


def run(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def init_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    run(repo, "init", "-b", "main")
    run(repo, "config", "user.name", "Autopoiesis Test")
    run(repo, "config", "user.email", "autopoiesis@example.invalid")
    (repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
    run(repo, "add", "tracked.txt")
    run(repo, "commit", "-m", "initial")
    return repo


class PrepareTaskTests(unittest.TestCase):
    def test_creates_ai_branch_when_conversation_is_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = init_repo(root)
            scratch = root / "scratch"
            scratch.mkdir()

            target, branch, created = prepare_task.prepare_task_branch(
                repo, scratch, "Add JSON output"
            )

            self.assertEqual(target, repo.resolve())
            self.assertEqual(branch, "ai/add-json-output")
            self.assertTrue(created)
            self.assertEqual(run(repo, "branch", "--show-current"), branch)

    def test_reuses_openhands_worktree_and_leaves_canonical_checkout_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = init_repo(root)
            worktree = root / "conversation"
            run(repo, "worktree", "add", "-b", "openhands/session-123", str(worktree))

            target, branch, created = prepare_task.prepare_task_branch(
                repo, worktree, "ignored task name"
            )

            self.assertEqual(target, worktree.resolve())
            self.assertEqual(branch, "openhands/session-123")
            self.assertFalse(created)
            self.assertEqual(run(repo, "branch", "--show-current"), "main")

    def test_refuses_to_reuse_different_task_branch_in_canonical_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = init_repo(root)
            scratch = root / "scratch"
            scratch.mkdir()
            run(repo, "switch", "-c", "ai/previous-task")

            with self.assertRaises(prepare_task.TaskBranchError):
                prepare_task.prepare_task_branch(repo, scratch, "next task")

            self.assertEqual(run(repo, "branch", "--show-current"), "ai/previous-task")

    def test_refuses_to_branch_from_dirty_fallback_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = init_repo(root)
            scratch = root / "scratch"
            scratch.mkdir()
            (repo / "tracked.txt").write_text("user change\n", encoding="utf-8")

            with self.assertRaises(prepare_task.TaskBranchError):
                prepare_task.prepare_task_branch(repo, scratch, "unsafe task")

            self.assertEqual(run(repo, "branch", "--show-current"), "main")


if __name__ == "__main__":
    unittest.main()
