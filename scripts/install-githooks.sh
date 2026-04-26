#!/bin/bash
# Activate the tracked git hooks under .githooks/ for this clone.
#
# Run once after a fresh clone. Idempotent — safe to re-run.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if [ ! -d .githooks ]; then
  echo "❌ .githooks/ not found at $REPO_ROOT" >&2
  exit 1
fi

git config core.hooksPath .githooks

# Ensure executable bits survive clones from filesystems that don't preserve them.
chmod +x .githooks/* 2>/dev/null || true

echo "✅ core.hooksPath = .githooks"
echo "   Active hooks:"
ls -1 .githooks/ | grep -v '^README' | sed 's/^/     /'
