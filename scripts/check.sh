#!/bin/sh
set -eu
task_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$task_root"
project_python=${PROJECT_PYTHON:-python3}
export PYTHONPATH="$task_root/src${PYTHONPATH:+:$PYTHONPATH}"
"$project_python" -m ruff check .
"$project_python" -m ruff format --check .
"$project_python" -m unittest discover -s tests -v
git diff --check
