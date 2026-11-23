#!/usr/bin/env bash
set -e

if [ -z "${GIT_AUTHOR_EMAIL:-}" ] || [ -z "${GIT_AUTHOR_NAME:-}" ]; then
    echo "WARN: GIT_AUTHOR_EMAIL/GIT_AUTHOR_NAME unset; skipping git identity setup" >&2
else
    git config --global user.email "${GIT_AUTHOR_EMAIL}"
    git config --global user.name "${GIT_AUTHOR_NAME}"
fi

# Fix SSH permissions (credential mount)
sudo chown -R vscode:vscode ~/.ssh || true
chmod 700 ~/.ssh 2>/dev/null || true
chmod 600 ~/.ssh/id_* ~/.ssh/*_ed25519 2>/dev/null || true
chmod 644 ~/.ssh/known_hosts ~/.ssh/config 2>/dev/null || true

# Fix gh permissions (credential mount)
sudo chown -R vscode:vscode ~/.config/gh 2>/dev/null || true
