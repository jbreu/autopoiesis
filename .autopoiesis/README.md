# Autopoiesis AI harness

OpenHands Agent Canvas runs in a container, works on the mounted repository,
and can deliver changes as commits and GitHub draft pull requests.
All commands below run from the repository root unless stated otherwise.

## Prerequisites and startup

- Docker Engine/Desktop with Compose v2 and Python 3.11+ for initial setup.
  On Windows, use WSL2 for the shell-based local checks.
- A model provider supported by OpenHands. Configure its model and credentials
  in the UI. Model calls may incur costs; model access is not included.

```bash
python3 .autopoiesis/scripts/init_env.py
docker compose -f .autopoiesis/compose.yaml up -d --build --wait --wait-timeout 180
```

The initializer creates `.autopoiesis/.env` with random keys and creates the
ignored `state`, `tmp`, and `cache` directories. Existing keys and state are
preserved. On Linux it uses your user/group IDs; run it as a regular user who
owns the checkout. On Windows, `python` can be used instead of `python3`.

Open [Agent Canvas](http://localhost:8000/canvas), configure the local backend,
a coding agent, and your model provider. The project path inside the container
is **`/projects/app`**, the full repository. If prompted for a backend key, use
LOCAL_BACKEND_API_KEY from `.autopoiesis/.env`.

OpenHands uses the root `AGENTS.md` as repository context. In this repository,
that file contains product-specific guidance and explicitly delegates harness
behavior to `.autopoiesis/AGENTS.md`. The Autopoiesis instruction contract
requires the agent to read and apply both files before every task. This keeps
product knowledge replaceable while the harness workflow remains reusable.

Compose reads `.env` beside this Compose file. Its explicit project name is
`autopoiesis`, preserving the original container identity after relocation.
You can also run `docker compose ...` from inside `.autopoiesis`.

## VS Code

Open the **`.autopoiesis` folder** in VS Code, then select **Dev Containers:
Reopen in Container**. Its `.devcontainer/devcontainer.json` uses this Compose
file and opens the full checkout at `/projects/app`. Run the initializer first.
Opening the repository root does not automatically discover the nested Dev
Container configuration.

## GitHub access

1. Set GH_TOKEN in the ignored `.autopoiesis/.env` locally. Use a token scoped to
   this repository with Contents: write and Pull requests: write; never paste it
   into prompts, commits, or chat.
2. Adjust AGENT_GIT_NAME and AGENT_GIT_EMAIL if needed.
3. Use an HTTPS origin without an embedded token:
   `git remote set-url origin https://github.com/jbreu/autopoiesis.git`.
4. Run `docker compose -f .autopoiesis/compose.yaml up -d --force-recreate`.
5. Verify with `docker compose -f .autopoiesis/compose.yaml exec agent gh auth status`.

The entrypoint configures Git identity and the GitHub credential helper.

## Frontend tasks, branches, and delivery

The full repository, including `.git`, is mounted at `/projects/app`. For the
strongest isolation, select `/projects/app` as the workspace in Agent Canvas
and use its new-worktree mode. Agent Canvas can then place the conversation on
its own `openhands/*` worktree.

The harness does not rely on that UI selection for branch safety. Before editing
files, the agent instructions require
`.autopoiesis/scripts/prepare_task.py <short-task-name>`. The helper reuses an
existing OpenHands worktree when it belongs to this repository. Otherwise it
falls back to the clean canonical checkout and creates an `ai/*` branch. It
refuses to continue from a dirty fallback checkout.

Task delivery is intentionally local-first:

- implementation and verification happen on the task branch;
- completed changes are committed locally;
- nothing is pushed to origin unless the user explicitly requests a push;
- a push request does not imply a pull request;
- a PR is created only when the user explicitly requests one, and that request
  also permits the prerequisite push.

Requested PRs are drafts. The agent never merges them or force-pushes.

See [the first task](docs/first-task.md) for an example. The canonical fallback
checkout supports one writing task at a time; parallel tasks should use separate
Agent Canvas worktrees.

## Checks

Inside the running container:

```bash
docker compose -f .autopoiesis/compose.yaml exec -T agent sh .autopoiesis/scripts/check.sh
docker compose -f .autopoiesis/compose.yaml exec -e PYTHONPATH=src agent python3 -m repo_demo "hello world"
```

Locally with a POSIX shell:

```bash
python3 -m venv .autopoiesis/.venv
.autopoiesis/.venv/bin/python -m pip install -r .autopoiesis/requirements-dev.txt
PROJECT_PYTHON=.autopoiesis/.venv/bin/python sh .autopoiesis/scripts/check.sh
```

The check script runs Ruff, application tests, harness regression tests, and
`git diff --check`. Ruff configuration and its cache are inside `.autopoiesis`.
GitHub's discoverable workflow remains in `.github/workflows/ci.yml`; it runs
these checks, builds the example package, and smoke-tests the container.
CI does not test model inference or GitHub writes.

## Operation and data

Run these commands **from `.autopoiesis`**:

- Status: `docker compose ps`
- Logs: `docker compose logs -f --tail=100 agent`
- Shell: `docker compose exec agent bash`
- Stop: `docker compose down`
- Rebuild after image changes: `docker compose up -d --build`
- Stop an active task through the UI, or stop all processes with `docker compose stop agent`.

Runtime directories are bind-mounted from this folder:

| Host directory | Container path | Contents |
| --- | --- | --- |
| `state/` | `/home/openhands/.openhands` | Sessions, settings, model credentials, automation data |
| `tmp/` | `/tmp` | Runtime temporary files and agent scratch files |
| `cache/` | `/home/openhands/.cache` | User tool caches |

These directories and `.env` are ignored by Git and excluded from the image build.
`docker compose down`, including `--volumes`, preserves the bind-mounted data.
Back up `state/` together with `.env`, and keep OH_SECRET_KEY unchanged so stored
credentials remain readable. Stop the container before copying state databases.
Restarts preserve sessions but do not guarantee automatic task resumption.

For a checkout using the previous layout, move the existing `.env` here before
initializing. Copy the stopped `autopoiesis_agent-state` volume into `state/`
before starting this layout. On Windows, perform the copy in Linux and expand
cache symlinks if the host cannot create them. Keep the old volume as a backup
until the migrated state is verified; it is no longer mounted by this Compose file.
When copying as root, restore state ownership to the AGENT_UID and AGENT_GID
configured in `.env` before starting the unprivileged container.

The UI binds only to localhost. For remote access, use an SSH tunnel such as
`ssh -L 8000:127.0.0.1:8000 user@server`. The Docker socket is not mounted.
See [architecture](docs/architecture.md) for responsibilities and limitations.

The harness is pinned to [OpenHands Agent Canvas](https://github.com/OpenHands/OpenHands)
1.20.0. System packages come from the base image's package repositories at build
time; reproducible builds would also require image digests and package snapshots.
