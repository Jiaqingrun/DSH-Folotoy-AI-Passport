---
name: passport-router
description: Classify a FoloToy AI Passport project as A/B/C, locate firmware and cover, and produce a bounded project card. Use before any build or publish step; read-only.
whenToUse: The user names an AI Passport project, asks what can be published, or hands over a repository/path for the first time.
---

# Route an AI Passport project

Do not write, build, or publish in this skill. Produce a project card first.

## 1. Resolve the root

- If the user gave a path, use it.
- Else use the session working directory.
- Run `git -C <root> rev-parse --show-toplevel`; if it succeeds, the git root is the project root.
- Do not scan the user's home directory or another project.

## 2. Run the scanner

Use the base directory the skill loader reports for this skill:

```bash
# macOS/Linux
python3 <base>/scripts/scan_project.py --root <root> --json

# Windows PowerShell
py -3 <base>/scripts/scan_project.py --root <root> --json
```

If the base directory is not shown, use glob to find `passport-router/SKILL.md`, then use its parent.

The scanner is read-only: it runs `git` queries, hashes files, and reads image headers. It does not build, flash, or upload.

## 3. Read the project's own rules

Read, in this order, if present:

1. `AGENTS.md`
2. `PROJECT.md`
3. `CMakeLists.txt`
4. `tools/validate.sh`
5. `docs/` index or README

The project's rules win over any family template. If a file is uncommitted/modified, say so; do not present it as the upstream baseline.

## 4. Classify

- **A**: `AGENTS.md` + `tools/validate.sh` + CMake/ESP-IDF + firmware binary + cover. Can build, validate, and prepare a submission.
- **B**: at least one publishable artifact (a built firmware binary or an exact 3:4 cover), but not a full A gate. Can inspect and build only with explicit user approval; publish only after the missing pieces are resolved.
- **C**: no firmware binary and no cover. Analyze/design only; refuse publish. A source-only firmware tree (CMake/main but no `.bin`) is C until it is built and rescanned; the scanner is read-only by design.

Output a card with: root, git remote, class, firmware candidates (path/bytes/sha256), cover candidates (path/WxH/bytes), missing items, and the single next action.

Never apply a class from a previous project to a new path.
