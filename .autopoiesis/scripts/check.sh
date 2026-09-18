#!/bin/sh
set -eu
harness_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
task_root=$(dirname -- "$harness_root")
cd "$task_root"
project_python=${PROJECT_PYTHON:-python3}
export PYTHONPATH="$task_root/src${PYTHONPATH:+:$PYTHONPATH}"
export RUFF_CACHE_DIR="$harness_root/cache/ruff"
"$project_python" -m ruff check --config "$harness_root/ruff.toml" .
"$project_python" -m ruff format --check --config "$harness_root/ruff.toml" .
"$project_python" -m unittest discover -s tests -v
"$project_python" -m unittest discover -s "$harness_root/tests" -v
git diff --check
