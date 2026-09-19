# Autopoiesis harness instructions

These instructions define how an AI development agent operates in this
repository. They complement the product-specific instructions in the repository
root `AGENTS.md`.

## Instruction contract

- Before starting any task, read both `/projects/app/AGENTS.md` and
  `/projects/app/.autopoiesis/AGENTS.md`.
- Apply both files together for every task, regardless of whether the requested
  change targets the product or the harness.
- The root `AGENTS.md` owns product behavior, product conventions, and
  product-specific verification.
- This file owns agent workflow, Git delivery, repository-wide verification,
  runtime behavior, and secret handling.
- For changes under `.autopoiesis/`, also read `.autopoiesis/README.md` and
  `.autopoiesis/docs/architecture.md`.
- Follow the user's concrete task and acceptance criteria while preserving the
  responsibilities above.

## Task workspace and branch

The canonical repository is mounted at `/projects/app`, including its `.git`
metadata. Every frontend task must make its changes on a task branch, never
directly on `main` or `master`.

Before modifying repository files, run this command from the conversation's
current working directory:

```bash
python3 /projects/app/.autopoiesis/scripts/prepare_task.py <short-task-name>
```

- If Agent Canvas already placed the conversation in an isolated
  `openhands/*` or `ai/*` worktree belonging to this repository, reuse it.
- Otherwise the helper falls back to the canonical `/projects/app` checkout,
  requires it to be clean, and creates `ai/<short-task-name>`.
- Continue all repository edits in the printed `AUTOPOIESIS_TASK_ROOT`.
- Treat a helper failure as a blocker. Do not work around a dirty checkout or
  modify a protected branch.
- The fallback checkout supports one writing task at a time. Parallel tasks
  require separate Agent Canvas worktrees.

Check the working tree before and after the task and preserve unrelated user
changes.

## Repository-wide verification

- Run `sh .autopoiesis/scripts/check.sh` after changes. In the container,
  `PROJECT_PYTHON` is already configured.
- Put agent scratch files in `.autopoiesis/tmp`, not in the repository root.
- Add or update tests appropriate to the change.
- Report exactly which checks ran and which could not run.
- Do not weaken existing tests or checks merely to obtain a passing result.

## Local commits and delivery

- Commit completed, verified task changes locally on the task branch. A local
  commit does not authorize any network write.
- By default, do **not** push and do **not** create a pull request.
- Only push when the user explicitly asks to push or otherwise explicitly asks
  to publish the change to the remote repository.
- A request to push authorizes `git push -u origin HEAD` only; it does not by
  itself authorize creating a pull request.
- Only create a pull request when the user explicitly asks for a PR. A PR
  request also authorizes the prerequisite push if the branch is not yet on
  origin.
- Create requested PRs as drafts against `main` and describe the problem,
  change, and verification results.
- Use
  `gh pr create --draft --base main --title ... --body-file .autopoiesis/tmp/pr-body.md`.
  Write real newlines to the body file.
- Do not merge a PR and do not force-push.
- If authentication is missing, retain the local commit and report the blocker.

## Runtime and security

- Never commit `.env`, credentials, session data, model transcripts, runtime
  state, caches, or temporary files.
- Do not print tokens or the contents of `.env` in terminal output or a PR.
- Preserve repository visibility, permissions, and branch-protection settings.
- Changes to `.autopoiesis/compose.yaml`, `.autopoiesis/Dockerfile.agent`, CI,
  or these instructions must be explicitly relevant to the current task and
  described in the PR.
- The running container does not rebuild itself after a Dockerfile edit.
- If three attempts at the same failure produce no progress, stop and describe
  the failure, evidence, and next useful action.
