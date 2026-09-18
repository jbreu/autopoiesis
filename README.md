# Autopoiesis example application

A small, dependency-free Python CLI for text statistics. Application code lives
in `src/repo_demo`, and its behavioral tests live in `tests`.

```bash
PYTHONPATH=src python3 -m repo_demo "hello world"
```

The output contains Characters, Words, and Lines. Characters are Unicode code
points; words are separated by whitespace. A trailing newline does not add an
empty line. Without a text argument, the CLI reads stdin. Requires Python 3.11+.

## AI development environment

The OpenHands harness, scripts, configuration, documentation, runtime state,
temporary files, and caches live in [.autopoiesis](.autopoiesis/README.md).
[AGENTS.md](AGENTS.md) contains the working instructions for this repository.
GitHub's CI entrypoint stays in `.github/workflows` so GitHub can discover it.

From the repository root:

```bash
python3 .autopoiesis/scripts/init_env.py
docker compose -f .autopoiesis/compose.yaml up -d --build --wait --wait-timeout 180
docker compose -f .autopoiesis/compose.yaml exec -T agent sh .autopoiesis/scripts/check.sh
```

Open [Agent Canvas](http://localhost:8000/canvas). For VS Code, open the
`.autopoiesis` folder and select **Dev Containers: Reopen in Container**.
The container opens the full repository at `/projects/app`.

See the [harness guide](.autopoiesis/README.md) for configuration, local checks,
GitHub access, and state backups.
