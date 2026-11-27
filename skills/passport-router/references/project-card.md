# Project card

Fields: root, gitRoot, remote, class (A/B/C), signals, firmware[] (path/bytes/sha256),
covers[] (path/bytes/width/height), dirty (tracked only), untracked, missing[].

- A: AGENTS.md + tools/validate.sh/.ps1/.cmd + firmware + exact 3:4 cover.
- B: firmware or exact 3:4 cover, but not both plus the gate.
- C: neither a firmware binary nor an exact 3:4 cover; analyze only.

Never infer class from source layout alone; run scan_project.py.
