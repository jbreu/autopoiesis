# Autopoiesis

A Git repository that includes its development environment and a coding agent.
OpenHands Agent Canvas runs in a container and is accessible through a browser.
The agent works on the mounted checkout, runs tests, and can deliver changes
as commits and GitHub pull requests.

The repository includes a small Python CLI for text statistics as an example.
It has no runtime dependencies. You can replace it with your own application
and adapt the container, working instructions, and CI accordingly.

## Prerequisites

- Git, Docker Engine/Desktop with Compose v2, and Python 3.11 or later for the
  initial local configuration. On Windows, run the commands in WSL2.
- Access to a model supported by OpenHands. Configure the provider, model, and
  API key in the UI on first launch. Model calls may incur costs; this repository
  includes neither model weights nor access to a model provider.
- For GitHub pushes and PRs: a token scoped to this repository with Contents: write
  and Pull requests: write. Local changes do not require a GitHub token.

## Getting started

Clone the repository and start the container:

```bash
git clone https://github.com/jbreu/autopoiesis.git
cd autopoiesis
python3 scripts/init_env.py
docker compose up -d --build --wait --wait-timeout 180
```

Open [Agent Canvas](http://localhost:8000/canvas). In the setup dialog, configure
the local backend server, a coding agent, and your model provider.
The project path **inside the container is `/projects/app`**. If prompted for a
backend key, use the locally generated LOCAL_BACKEND_API_KEY value from .env.
Explicitly ask the agent to read AGENTS.md when assigning its first task.

`scripts/init_env.py` creates .env with random keys and matching user IDs on
Linux. It leaves an existing file unchanged. If your Linux checkout is owned
by root, change its ownership to a regular user; the container runs as the
unprivileged openhands user.

## Enabling GitHub access

1. Set GH_TOKEN in the ignored .env file. Enter the token locally; do not copy
   it into an agent prompt, commit, or chat.
2. Adjust AGENT_GIT_NAME and AGENT_GIT_EMAIL if needed.
3. Use an HTTPS URL without an embedded token for origin:
   `git remote set-url origin https://github.com/jbreu/autopoiesis.git`.
4. Run `docker compose up -d --force-recreate`.
5. Verify access using `docker compose exec agent gh auth status` and
   `docker compose exec agent git remote -v`.

The entrypoint configures the Git identity and GitHub credential helper. The
agent can then commit and push with git and create PRs with gh. The working
instructions require a new ai/* branch per task and a draft PR as the result.
Configure branch protection for main separately on GitHub; AGENTS.md provides
working instructions and does not enforce GitHub permissions.

## First agent task

See [docs/first-task.md](docs/first-task.md) for a complete example task:
add JSON output to the CLI, including tests and a draft PR.
This feature is intentionally not implemented yet and serves as the first real
development task. The web interface and terminal share the same checkout;
start with only one task writing to it at a time.

## Tests and example application

Inside the running container:

```bash
docker compose exec agent sh scripts/check.sh
docker compose exec -e PYTHONPATH=src agent python3 -m repo_demo "hello world"
```

Locally, without a container:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
PROJECT_PYTHON=.venv/bin/python sh scripts/check.sh
PYTHONPATH=src .venv/bin/python -m repo_demo "hello world"
```

The output contains Characters, Words, and Lines. Characters are counted as
Unicode code points; words are separated by whitespace. A trailing newline
does not add an extra empty line. Without a text argument, the CLI reads stdin.

## Operation

- Status: `docker compose ps`
- Logs: `docker compose logs -f --tail=100 agent`
- Shell: `docker compose exec agent bash`
- Stop: `docker compose down`
- After changing the image: `docker compose up -d --build`
- Stop an active task through the UI; use `docker compose stop agent` to stop
  all processes.

Sessions, settings, and model credentials are stored in the named agent-state
volume. `docker compose down` preserves this volume. `docker compose down --volumes`
deletes the state and should only be used for an intentional reset. Keep the
OH_SECRET_KEY value together with the volume; do not regenerate it arbitrarily.

By default, the UI is only accessible through localhost. For a remote server,
start with an SSH tunnel, for example
`ssh -L 8000:127.0.0.1:8000 user@server`. The container mounts only this checkout
and its state volume. It does not mount the host's Docker socket; Docker builds
run in CI or on the host.

## CI and development environment

GitHub Actions runs the same checks through scripts/check.sh, builds the Python
package, and also starts the agent image. The container test checks the web UI,
toolchain, and write access. It uses neither real model keys nor GitHub write
permissions, so it does not test LLM inference or PR creation.

You can open the existing Compose environment with VS Code / Dev Containers.
Run scripts/init_env.py first. Restarting the container makes existing sessions
available; this PoC does not guarantee automatic resumption of interrupted tasks.

## Structure and next steps

See [docs/architecture.md](docs/architecture.md) for responsibilities and limitations.
Possible extensions include chat adapters, a task queue, and automatic task
selection. Initially, the PoC is controlled through explicit tasks in the browser.

Upstream: [OpenHands](https://github.com/OpenHands/OpenHands),
[Docker deployment](https://docs.openhands.dev/openhands/usage/agent-canvas/backend-setup/docker),
[first-time setup](https://docs.openhands.dev/openhands/usage/agent-canvas/first-time-setup).
The harness is pinned to Agent Canvas 1.20.0. System packages are installed from
the base image's package repository at build time; byte-for-byte reproducible
builds would also require image digests and package snapshots.
