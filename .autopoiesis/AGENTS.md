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

## Repository-wide verification

- Run `sh .autopoiesis/scripts/check.sh` after changes. In the container,
  `PROJECT_PYTHON` is already configured.
- Put agent scratch files in `.autopoiesis/tmp`, not in the repository root.
- Report exactly which checks ran and which could not run.
- Do not weaken existing tests or checks merely to obtain a passing result.

## Git workflow

- Use one task at a time in this checkout and create a new
  `ai/<short-task-name>` branch.
- Check the working tree first and preserve unrelated user changes.
- Commit only files belonging to the task, using explicit file paths when
  staging.
- When the user requests delivery through GitHub, push the task branch and open
  a draft PR describing the problem, change, and verification results.
- Use
  `gh pr create --draft --base main --title ... --body-file .autopoiesis/tmp/pr-body.md`.
  Write real newlines to the body file.
- Do not merge the PR and do not force-push.
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
