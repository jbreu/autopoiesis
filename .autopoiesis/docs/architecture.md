# Architecture

## Workflow

1. The user assigns a task in Agent Canvas.
2. OpenHands loads the root AGENTS.md as repository context. The instruction
   contract in that file and .autopoiesis/AGENTS.md requires both files to be
   read and applied together.
3. The harness reads the project in /projects/app and communicates with the selected
   model provider. File access, code execution, and Git commands run inside the container.
4. The agent works on an ai/* branch and runs .autopoiesis/scripts/check.sh.
5. With GH_TOKEN configured, it can push the branch and create a draft PR.
6. GitHub Actions checks the code and container; the user decides whether to merge.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| src/repo_demo and tests | Example application and behavioral tests |
| .autopoiesis/Dockerfile.agent | OpenHands base image, Python tools, and GitHub CLI |
| .autopoiesis/compose.yaml | Local startup, workspace, resources, and persistent data |
| AGENTS.md | Product-specific behavior, conventions, and product verification |
| .autopoiesis/AGENTS.md | Agent workflow, Git delivery, runtime, security, and repository-wide verification |
| .autopoiesis/scripts/check.sh | Shared checks for developers, agents, and CI |
| .autopoiesis/tests | Harness initialization regression tests |
| .autopoiesis/state, tmp, cache | Ignored runtime data, temporary files, and caches |
| .github/workflows/ci.yml | Independent checks on the CI runner |
| .autopoiesis/.devcontainer/devcontainer.json | Optional interactive IDE access |

Paths in this table are relative to the repository root. Open .autopoiesis in
VS Code to discover its Dev Container; the container workspace is still the
full repository. GitHub requires its workflow entrypoint in .github/workflows.
The root AGENTS.md remains the repository-context entrypoint. It points the agent
to .autopoiesis/AGENTS.md, while the harness file points back to the root file.
Harness regression tests verify that this two-file instruction contract remains
connected.

## Why project tools are installed separately

OpenHands includes its own Python environment. The example installs its
development tools in /opt/poc-tools and explicitly uses PROJECT_PYTHON.
The harness PATH is preserved so its entrypoint can still find the original
packages. The custom entrypoint adds Git configuration and then starts the
official OpenHands entrypoint.

## State and limitations

The entire checkout, including .git, is mounted with write access. Commits
therefore survive container restarts even without a push. The .autopoiesis/.env file is
local and ignored by Git; the agent can generally read the container environment
and mounted files. A separate token scoped to this repository limits its GitHub
access. Containerization does not protect secrets that the agent can read.

The .autopoiesis/state bind mount contains sessions, settings, and model
credentials. It is not part of Git history. Moving to a new machine requires
the repository, .autopoiesis/.env, and a stopped-state backup to preserve sessions.
The old autopoiesis_agent-state volume is not used by this layout.

The container's /tmp and user cache are also bind-mounted under .autopoiesis.
TMPDIR, TMP, TEMP, and XDG_CACHE_HOME point to those mounts. Agent instructions
put scratch files in .autopoiesis/tmp. This directs standard temporary-file APIs
and explicit /tmp writes into the harness directory; an agent can still write
elsewhere in the checkout. The image build context is only .autopoiesis and its
allowlist excludes runtime state, secrets, caches, and temporary files.

The health check verifies the web UI's HTTP response and Content-Type, as well
as the backend's /ready endpoint. An actual model task and GitHub push require
your own credentials and are intended to be checked in a manual end-to-end test.
The maximum number of repair attempts in .autopoiesis/AGENTS.md is an
instruction; enforcing a task time limit requires an external dispatcher.

## Future extensions

- Chat: an authenticated adapter maps a chat to an agent session.
- Queue: stores the task, starting commit, branch, session ID, and status.
- Parallel execution: a separate clone or worktree per task, with no shared
  working copy being modified concurrently.
- Automation: explicit issues/labels or CI events provide tasks; enforce runtime
  and budget limits outside the mutable checkout.
- GitLab: replace Git access and PR helpers with the corresponding GitLab configuration.
