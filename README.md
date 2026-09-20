# Autopoiesis

from Greek αὐτo- (auto) 'self' and ποίησις (poiesis) 'creation, production'

Autopoiesis is a repository concept/pattern for keeping an AI development harness next to the product it develops.

The central idea is simple: a modern code repository typically contains a lot of meta files like CI config, devcontainers and nowadays the inevitable AI skills etc. So why not go a step further and include also the AI tooling like an agentic frontend itself? This projects explores that very idea.

The harness in this repository is intentionally colocated with the code under [`.autopoiesis/`](.autopoiesis/README.md). It runs OpenHands Agent Canvas in a container, mounts the full Git checkout, executes repository checks, creates commits, and can push task branches and open GitHub draft pull requests. The user can clone the repo, launch the Autopoiesis setup and immediately has a functional agentic coding setup, tuned for the respective repository.

The example application under `src/` exists only to make the pattern executable. It is replaceable and is not the focus of this repository.

## Concept

A conventional repository usually assumes a human developer already has the right tools, context, workflow knowledge, and credentials.

Autopoiesis makes those assumptions explicit and version-controlled:

- **Environment**:containerized agent runtime that can work on the complete checkout.
- **Repository knowledge**: agent instructions stored with the repository.
- **Verification**: the same checks can be run by humans, agents, and CI.
- **Delivery workflow**: agents work on isolated task branches and deliver changes through draft pull requests.
- **Persistent local state**: sessions, settings, caches, and temporary files stay outside Git history but inside the harness directory.
- **Human control**: the agent may prepare changes, but CI and the repository owner remain the final gate (subject to configuration)

This makes the repository itself carry much of the setup required to continue developing it with an AI agent.

## Why Autopoiesis?

For organizations adopting AI coding agents across multiple teams, this pattern offers several potential benefits:

| Benefit                           | Organizational value                                                                                                                                                                      |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Harmonized AI harnesses           | Teams can share tools, interfaces, and delivery workflows while retaining project-specific configuration.                                                                                 |
| Reproducible environments         | Versioned container configuration and pinned dependencies reduce differences between individual setups and make environment changes reviewable.                                           |
| Governance as code                | Working rules, verification commands, and delivery policies live in Git and can evolve through pull requests. Critical rules also need enforcement outside agent instructions.            |
| Shared project knowledge          | Architecture guidance, build instructions, and conventions remain available to developers and agents rather than being repeatedly reconstructed in personal chats.                        |
| Traceable changes                 | Task branches, commits, diffs, and test results support review. Linking the original task and agent run to the resulting change can provide a more complete record.                       |
| Faster onboarding                 | A common repository entrypoint gives new developers and agents access to the same environment and documented procedures.                                                                  |
| Less duplicated infrastructure    | A platform team can maintain common runtime, Git integration, and verification mechanisms instead of each product team building its own.                                                  |
| Defined enterprise integrations   | The harness provides a place to configure approved model access, internal package sources, identities, and CI integrations. These integrations still need to be implemented and operated. |
| Flexible interfaces and providers | Repository-owned instructions and workflows can support different task entrypoints and model backends, provided their integration contracts are maintained.                               |
| Reviewable self-improvement       | Agents can propose improvements to tests, documentation, automation, and the harness itself through the same review process used for product changes.                                     |

### Shared standards with project ownership

A corporate deployment could combine a centrally maintained, versioned harness core with repository-specific build commands, tests, and architecture guidance. The separation between `.autopoiesis/` and product files supports this division of responsibilities: platform teams maintain shared capabilities while product teams own their product's behavior and acceptance criteria.

The combined instructions in `AGENTS.md` and `.autopoiesis/AGENTS.md` expresses this separation within the current repository. Distributing a shared core across repositories, managing upgrades, and preventing configuration drift would require an additional maintenance process; they are not automated by this proof of concept.

## Implementation

The implementation is centered around `.autopoiesis/`:

```text
.
├── .autopoiesis/
│   ├── docs/                # harness architecture and usage
│   ├── scripts/             # initialization, checks, smoke tests
│   ├── tests/               # harness regression tests
│   ├── Dockerfile.agent     # agent runtime image
│   ├── compose.yaml         # workspace, state and runtime wiring
│   ├── requirements-dev.txt
│   └── README.md            # detailed harness operation
├── .devcontainer/           # discoverable VS Code entrypoint (optional)
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

Then open http://localhost:8000/canvas.

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

At the moment, the Autopoiesis and the demostrator are setup in one repo. A more polished setup seperates the Autopoiesis generic code to one repo, while its adoption for a specific (demo) repo is seperate.