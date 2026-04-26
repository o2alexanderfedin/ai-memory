# 3rd-party — Research Subjects

This directory holds external repositories we're studying as part of ongoing
research, plus our notes about each one. The external code itself is **not**
tracked in this repo (each clone has its own git history); only our curation
artifacts (`README.md`, `INDEX.md`, `notes/`) are committed.

## Why this exists

Research investigations under `docs/reports/` (e.g.
`synthius-mem-scientific-investigation/`) frequently need to inspect, build,
or run external projects. Cloning those projects into `docs/reports/.../`
pollutes the documentation tree with hundreds of MB of unrelated source
trees. This directory is the canonical location for those clones, separate
from our own source (`src/`) and from the research write-ups (`docs/`).

## Layout

```
3rd-party/
├── README.md          ← this file (convention)
├── INDEX.md           ← registry of every clone living here
├── .gitignore         ← ignores every subdirectory except notes/
├── notes/             ← project-owned notes about external code
│   └── <subject>.md   ← one note file per research subject
└── <subject>/         ← cloned external repo (gitignored)
    └── … (upstream's own files, including its own .git)
```

## Adding a new research subject

1. **Clone** into a subdirectory named after the upstream project:
   ```bash
   cd 3rd-party
   git clone <upstream-url> <subject-name>
   ```
   Use kebab-case for `<subject-name>`. Optionally suffix with the focus
   area (e.g. `hupyy-cpp-to-rust` rather than just `hupyy`).

2. **Register it** in [INDEX.md](INDEX.md) — one row with: name, upstream URL,
   commit/tag pinned, related research doc, date added, one-line purpose.

3. **Take notes** in `notes/<subject-name>.md`. Anything you'd want to find
   later: build steps you figured out, surprising findings, files worth
   re-reading, links into the upstream code by path. The clone is
   gitignored, but your notes are committed.

4. **Cross-link** from the research doc that motivated the clone (e.g. an
   evidence file under `docs/reports/.../evidence/`) back to your notes
   here, so future readers can trace why this subject is on disk.

## Removing a subject

When research wraps up:
- Keep `notes/<subject-name>.md` (it's project memory).
- Update INDEX.md status to `archived` and note the closing research doc.
- Delete the clone with `rm -rf <subject-name>/` (it's gitignored, so this
  is local-only).

## Conventions

- **No commits inside the clones.** If you need to patch upstream, do it on
  a branch in their repo and record what you did in `notes/<subject>.md`.
- **Pin a commit** in INDEX.md so a future re-clone can reproduce findings.
- **Don't `cd` into a subject and run our build tooling against it** — these
  are read-only references, not part of our build graph.
