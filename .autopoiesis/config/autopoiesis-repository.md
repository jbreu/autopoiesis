---
name: autopoiesis-repository
description: Repository location and instruction entrypoints for this Autopoiesis deployment.
---

The repository for this deployment is mounted at `/projects/app`, including
its Git history, product source, tests, and Autopoiesis harness.

Agent Canvas may start a conversation in an empty scratch repository under
`/home/openhands/workspace/project/`. That directory is not the product checkout.
For repository questions and development tasks, inspect `/projects/app` unless
the user explicitly selects another repository. If the current workspace is
already a Git worktree of `/projects/app`, use that worktree for the task.

Before starting a repository task, read and apply both
`/projects/app/AGENTS.md` and `/projects/app/.autopoiesis/AGENTS.md`.
They define product behavior and the harness workflow, including selecting a
safe task branch before edits. Follow their task-workspace selection instructions.
