#!/bin/sh
set -eu
git config --global user.name "${AGENT_GIT_NAME:-AI Development Bot}"
git config --global user.email "${AGENT_GIT_EMAIL:-ai-dev-bot@example.invalid}"
git config --global --add safe.directory /projects/app
if [ -n "${GH_TOKEN:-}" ]; then
    gh auth setup-git --hostname github.com
fi
exec /opt/agent-canvas/entrypoint.sh "$@"
