# Tracked git hooks

These hooks are tracked in the repo and activated via `core.hooksPath`. They
enforce the git-flow workflow locally:

- **`pre-commit`** — refuses commits on `main` or `develop`. Warns on branches
  that don't match `feature/`, `release/`, `hotfix/`, or `bugfix/`.
- **`pre-push`** — refuses direct pushes to `main` or `develop`. Catches
  commits that arrive via merge/rebase rather than direct edit.

## Activate after a fresh clone

Hook tracking via `core.hooksPath` is per-clone — git won't pick up `.githooks/`
automatically. Run once after cloning:

```bash
./scripts/install-githooks.sh
# or directly:
git config core.hooksPath .githooks
```

## Bypass (rare, deliberate)

```bash
git commit --no-verify   # skip pre-commit
git push   --no-verify   # skip pre-push
```

Don't make a habit of it. The hooks exist because direct merges to `main`
without a PR have historically caused regressions.
