# Working in this repository

This repository contains both the example application and the environment used
to develop it. Read README.md and docs/architecture.md before changing the harness.

## Scope and verification

- Follow the user's concrete task and acceptance criteria.
- Use English for repository documentation, code comments, and user-facing text.
- Application code is in src/repo_demo; behavioral tests are in tests.
- Preserve the documented CLI behavior unless the task asks to change it.
- Keep the example's runtime dependency-free where practical.
- Run `sh scripts/check.sh` after changes. In the container PROJECT_PYTHON is set.
- Use a regression test when fixing an observable bug. Do not weaken existing
  assertions merely to obtain a passing result.
- Report exactly which checks ran and which could not run.

## Git workflow

- Use one task at a time in this checkout and a new `ai/<short-task-name>` branch.
- Check the working tree first. Preserve unrelated user changes.
- Commit only files belonging to the task, using explicit file paths when staging.
- When the user requests delivery through GitHub, push the task branch and open a
  draft PR with the problem, change and verification results. The container has gh.
- Use `gh pr create --draft --base main --title ... --body-file /tmp/pr-body.md`.
  Write real newlines to the body file. Do not merge the PR or force-push.
- If authentication is missing, retain the local commit and report the blocker.

## Runtime configuration

- Never commit .env, credentials, session data or model transcripts.
- Do not print tokens or the contents of .env in terminal output or a PR.
- Preserve repository visibility, permissions and branch protection settings.
- Changes to compose.yaml, Dockerfile.agent, CI or these instructions must be
  explicitly relevant to the current task and described in the PR.
- The running container does not rebuild itself after a Dockerfile edit.
- If three attempts at the same failure produce no progress, stop and describe
  the failure, evidence and next useful action.
