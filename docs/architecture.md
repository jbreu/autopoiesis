# Architecture

## Workflow

1. The user assigns a task in Agent Canvas.
2. The harness reads the project in /projects/app and communicates with the selected
   model provider. File access, code execution, and Git commands run inside the container.
3. The agent works on an ai/* branch and runs scripts/check.sh.
4. With GH_TOKEN configured, it can push the branch and create a draft PR.
5. GitHub Actions checks the code and container; the user decides whether to merge.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| src/repo_demo and tests | Example application and behavioral tests |
| Dockerfile.agent | OpenHands base image, Python tools, and GitHub CLI |
| compose.yaml | Local startup, workspace, resources, and persistent data |
| AGENTS.md | Project knowledge and agreed workflow |
| scripts/check.sh | Shared checks for developers, agents, and CI |
| .github/workflows/ci.yml | Independent checks on the CI runner |
| .devcontainer/devcontainer.json | Optional interactive IDE access |

## Why project tools are installed separately

OpenHands includes its own Python environment. The example installs its
development tools in /opt/poc-tools and explicitly uses PROJECT_PYTHON.
The harness PATH is preserved so its entrypoint can still find the original
packages. The custom entrypoint adds Git configuration and then starts the
official OpenHands entrypoint.

## State and limitations

The entire checkout, including .git, is mounted with write access. Commits
therefore survive container restarts even without a push. The .env file is
local and ignored by Git; the agent can generally read the container environment
and mounted files. A separate token scoped to this repository limits its GitHub
access. Containerization does not protect secrets that the agent can read.

The volume contains sessions, settings, and model credentials. It is not part of
the Git history. Moving to a new machine requires the repository, runtime
configuration, and a volume backup if you want to preserve sessions.

The health check verifies the web UI's HTTP response and Content-Type, as well
as the backend's /ready endpoint. An actual model task and GitHub push require
your own credentials and are intended to be checked in a manual end-to-end test.
The maximum number of repair attempts in AGENTS.md is an instruction; enforcing
a task time limit requires an external dispatcher.

## Future extensions

- Chat: an authenticated adapter maps a chat to an agent session.
- Queue: stores the task, starting commit, branch, session ID, and status.
- Parallel execution: a separate clone or worktree per task, with no shared
  working copy being modified concurrently.
- Automation: explicit issues/labels or CI events provide tasks; enforce runtime
  and budget limits outside the mutable checkout.
- GitLab: replace Git access and PR helpers with the corresponding GitLab configuration.
