# Autopoiesis

Autopoiesis is a repository pattern for keeping an AI development harness next to the product it develops.

The central idea is simple: a repository should contain not only product code, but also the environment, instructions, checks, and Git workflow an AI coding agent needs to work on that product safely and reproducibly.

The harness in this repository is intentionally colocated with the code under [`.autopoiesis/`](.autopoiesis/README.md). It runs OpenHands Agent Canvas in a container, mounts the full Git checkout, executes repository checks, creates commits, and can push task branches and open GitHub draft pull requests.

The example application under `src/` exists only to make the pattern executable. It is replaceable and is not the focus of this repository.

## Concept

A conventional repository usually assumes a human developer already has the right tools, context, workflow knowledge, and credentials.

Autopoiesis makes those assumptions explicit and version-controlled:

- **Environment** — a containerized agent runtime that can work on the complete checkout.
- **Repository knowledge** — agent instructions stored with the repository.
- **Verification** — the same checks can be run by humans, agents, and CI.
- **Delivery workflow** — agents work on isolated task branches and deliver changes through draft pull requests.
- **Persistent local state** — sessions, settings, caches, and temporary files stay outside Git history but inside the harness directory.
- **Human control** — the agent may prepare changes, but CI and the repository owner remain the final gate.

This makes the repository itself carry much of the information required to continue developing it with an AI agent.

## Implementation

The implementation is centered around `.autopoiesis/`:

```text
.
├── .autopoiesis/
│   ├── .devcontainer/       # optional VS Code entrypoint
│   ├── docs/                # harness architecture and usage
│   ├── scripts/             # initialization, checks, smoke tests
│   ├── tests/               # harness regression tests
│   ├── Dockerfile.agent     # agent runtime image
│   ├── compose.yaml         # workspace, state and runtime wiring
│   ├── requirements-dev.txt
│   └── README.md            # detailed harness operation
├── .github/workflows/ci.yml # independent GitHub CI entrypoint
├── AGENTS.md                # repository/product instructions
├── src/                     # replaceable example product
└── tests/                   # replaceable product tests
```

The container sees the repository at `/projects/app`, including its `.git` directory. This allows the agent to modify files, run tests, create branches and commits, and use the GitHub CLI.

Runtime data is kept under ignored paths inside `.autopoiesis/`:

```text
.autopoiesis/state/
.autopoiesis/tmp/
.autopoiesis/cache/
.autopoiesis/.env
```

They hold OpenHands state, temporary files, caches, and local secrets without mixing them into the product source tree or Git history.

## Development flow

A typical task follows this path:

```text
task
  ↓
Agent Canvas / coding agent
  ↓
read repository instructions
  ↓
create ai/<task> branch
  ↓
modify product or harness
  ↓
run repository checks
  ↓
commit + push
  ↓
draft pull request
  ↓
GitHub Actions
  ↓
human review / merge
```

The current setup deliberately stops before autonomous merging. The agent can prepare and deliver a change; acceptance remains an external decision.

## Running the harness

Prerequisites are Docker with Compose v2 and Python 3.11+ for initialization.

From the repository root:

```bash
python3 .autopoiesis/scripts/init_env.py
docker compose -f .autopoiesis/compose.yaml up -d --build --wait --wait-timeout 180
```

Then open [Agent Canvas](http://localhost:8000/canvas).

The complete operational guide, including model configuration, GitHub access, local checks, persistent state, and backup behavior, is in [`.autopoiesis/README.md`](.autopoiesis/README.md).

## Verification

The shared check entrypoint is:

```bash
sh .autopoiesis/scripts/check.sh
```

It is used by the local development environment and GitHub Actions. CI also builds and smoke-tests the agent container.

The CI intentionally does not execute paid model inference or perform live GitHub writes.

## Design boundaries

The current proof of concept has several deliberate boundaries:

- One writable checkout is used at a time; parallel tasks need separate worktrees or clones.
- The mounted repository is writable by the agent, so containerization is not a security boundary for repository contents or readable secrets.
- GitHub credentials should be scoped to this repository and supplied only through the ignored local environment.
- The agent is instructed not to merge its own pull requests.
- Runtime and model-budget enforcement would require an external dispatcher rather than instructions inside the mutable checkout.

These constraints keep the first implementation small while preserving a path toward more autonomous operation.

## Direction

The next layer is orchestration around the existing harness: task queues, issue or chat adapters, per-task worktrees, runtime and cost limits, and event-driven agent execution.

That would move Autopoiesis from a self-contained **AI development environment** toward a repository that can continuously receive work, prepare changes, verify them, and propose its own evolution while retaining explicit human governance.
