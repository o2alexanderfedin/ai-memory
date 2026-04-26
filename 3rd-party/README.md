# 3rd-party — Research Subjects

This directory holds external repositories we're studying as part of ongoing
research, plus our notes about each one. Each external repo is added as a
**git submodule** so the parent repo records both the upstream URL and the
exact commit we surveyed; the submodule's working tree is reproducible by any
future clone of this repo.

## Why this exists

Research investigations under `docs/reports/` (e.g.
`synthius-mem-scientific-investigation/`) frequently need to inspect, build,
or run external projects. Cloning those projects into `docs/reports/.../`
pollutes the documentation tree with hundreds of MB of unrelated source
trees. This directory is the canonical location for those references,
separate from our own source (`src/`) and from the research write-ups
(`docs/`).

## Layout

```
3rd-party/
├── README.md          ← this file (convention)
├── INDEX.md           ← registry of every submodule living here
├── CLAUDE.md          ← short directive for AI assistants
├── .gitignore         ← intentionally empty (submodules track themselves)
├── notes/             ← project-owned notes about external code
│   ├── <subject>.md   ← one note file per research subject
│   └── <research>/    ← multi-subject research projects (sub-directory)
└── <subject>/         ← git submodule (URL + pinned commit tracked in .gitmodules)
    └── … (upstream's own files at the pinned commit)
```

## Adding a new research subject

1. **Add as submodule** from the repo root:
   ```bash
   cd <repo-root>
   git submodule add <upstream-url> 3rd-party/<subject-name>
   git -C 3rd-party/<subject-name> checkout <commit-or-tag>   # pin
   git add 3rd-party/<subject-name>                            # records pinned commit
   ```
   Use kebab-case for `<subject-name>`. Optionally suffix with the focus
   area (e.g. `hupyy-cpp-to-rust` rather than just `hupyy`). For gists, the
   `.git` URL works (e.g.
   `https://gist.github.com/<user>/<id>.git`).

2. **Register it** in [INDEX.md](INDEX.md) — one row with: name, upstream
   URL, pinned commit (the one in `.gitmodules`), related research doc, date
   added, one-line purpose.

3. **Take notes** in `notes/<subject-name>.md`. Anything you'd want to find
   later: build steps, surprising findings, files worth re-reading, links
   into the upstream code by path. Notes are tracked in this repo even
   though the submodule's content lives in its own history.

4. **Cross-link** from the research doc that motivated the addition (e.g. an
   evidence file under `docs/reports/.../evidence/`) back to your notes
   here, so future readers can trace why this subject is on disk.

## Cloning the parent repo with all submodules

Anyone (including a remote agent) checking out this repo gets the
submodules with one of:

```bash
git clone --recurse-submodules <parent-url>
# or, after a plain clone:
git submodule update --init --recursive
```

Without that flag, the submodule directories will exist but be empty.

## Removing a subject

When research wraps up:
- Keep `notes/<subject-name>.md` (it's project memory).
- Update INDEX.md status to `archived` and note the closing research doc.
- Remove the submodule:
  ```bash
  git submodule deinit -f 3rd-party/<subject-name>
  git rm -f 3rd-party/<subject-name>
  rm -rf .git/modules/3rd-party/<subject-name>
  ```

## Conventions

- **Submodules only — don't plain-clone here.** A loose `git clone` would
  bring an unrelated `.git` directory into the parent's working tree
  without tracking the URL or commit. Always use `git submodule add`.
- **No commits inside the submodules.** If you need to patch upstream, do
  it on a branch in their repo and record what you did in
  `notes/<subject>.md`.
- **Update the pinned commit deliberately.** `git submodule update --remote`
  bumps a submodule to its branch HEAD; commit the resulting `.gitmodules`
  pointer change with a message that explains why we re-pinned.
- **Don't run our build tooling against a submodule's tree** — these are
  read-only references, not part of our build graph.
