---
name: passport-code-audit
description: Strict post-implementation audit of FoloToy AI Passport firmware for project/security compliance and runtime smoothness before declaring completion, device acceptance, or publishing. Not for initial implementation, build-only checks, or flashing.
---

<p align="right"><a href="SKILL.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Strict Audit After Firmware Completion

Run this audit **after the firmware implementation is complete** and before the
agent says the work is done, hands it to device testing, or publishes it. It is
not optional because the build passed. It does not replace the build gate or
physical-device acceptance; it adds an evidence-based review of the code that
those gates do not perform.

Read the project's `AGENTS.md`, `PROJECT.md`, AI development guide, contribution
and security rules, and the relevant build/test guide first. Resolve the project
root with `git rev-parse --show-toplevel`; do not audit the installed skill
folder.

## 1. Freeze the candidate

1. Record `git rev-parse HEAD`, `git status --short --branch`, the task scope,
   and the exact build command. Do not commit, push, or flash as part of the
   audit.
2. Identify changed files and their callers. Audit the changed behavior and any
   shared code whose contract it changes; do not sweep unrelated failures into
   this task.
3. Record the firmware identity and the device/serial artifact when available.
   A stale or unidentifiable binary cannot be audited as the candidate.

## 2. Run the repository gates, then collect signals

Run the project's documented gates, at minimum:

```bash
./tools/validate.sh --static
# Activate the required ESP-IDF environment first:
./tools/validate.sh
```

Run host tests required by the change, and the scanner below from the audit
skill base directory:

```bash
python3 <base>/scripts/scan_code.py --root <project-root> --json
# Windows: py -3 <base>\scripts\scan_code.py --root <project-root> --json
```

The scanner is **advisory**. It reports unsafe calls, heap calls, blocking
delays, full-screen invalidations, secret-like literals, and open markers; it
cannot prove memory safety or smoothness. Review every hit in context and never
report "clean output" as a passed audit by itself.

## 3. Compliance review

Review all changed code and its integration points against
[`references/checklist.md`](references/checklist.md):

- **Memory and bounds:** ownership, lifetime, bounds, integer overflow, null and
  error paths, stack/heap limits, no use-after-free or unbounded growth.
- **Concurrency and UI:** LVGL lock held correctly and briefly, no blocking
  flash/network/file/serial work inside render or input callbacks, task stacks
  and priorities, watchdog-safe loops, clean teardown.
- **Security and secrets:** no credentials/tokens/device secrets in source,
  logs, screenshots, or committed captures; no unsafe command execution;
  network/TLS and input validation appropriate to the feature.
- **Project/legal compliance:** repository rules, licenses and third-party
  notices, generated artifacts, no disabled checks or suppressed warnings, no
  debug leftovers, no unapproved dependency or partition change.
- **Recovery:** failure states are visible and bounded; no infinite retry,
  silent fallback, or destructive repair path.

## 4. Smoothness and runtime review

Static review does not establish fluidity. Define or reuse the Gate 0 budgets,
then measure the installed candidate on the real device in representative
scenes, warming up and sampling for the agreed duration:

| Measurement | Required evidence |
| --- | --- |
| Frame cadence | render/display timing or panel-completion cadence; dropped frames |
| Input response | UP/DOWN/OK short/long/double latency and missed/duplicated actions |
| Memory | free/minimum heap, largest free block, PSRAM where present |
| Stability | watchdog resets, allocation failures, crashes, black frames, tearing |
| Hot path | no busy loop, per-frame allocation, long delay, full redraw, or blocking log |

Use the project's thresholds. If none exist, record explicit budgets before
measurement instead of declaring an unmeasured "smooth" result. A serial
screenshot proves pixels, not animation; keep it as visual evidence alongside
the measurements. If device access is unavailable, report `NOT RUN`, not PASS.

## 5. Severity and blocking rule

- **P0:** crash, corruption, secret exposure, security or license violation,
  unbounded memory, disabled safety gate. Blocks completion and publishing.
- **P1:** reproducible jank/freeze, input loss, blocking UI path, leak, watchdog
  risk, misleading failure handling. Blocks completion and publishing.
- **P2:** maintainability or non-blocking documentation issue. Record it; may be
  deferred with the user's decision.

Fix P0/P1 findings, rerun affected tests, build, capture, and measurements, then
repeat the audit. Do not downgrade a finding to make the gate pass, and do not
claim a clean audit while a required gate is `FAIL` or `NOT RUN`.

## 6. Write the audit record

Create a concise record (for example `docs/audits/<candidate>-code-audit.md`)
with the candidate identity, commands and results, findings table, measurements,
and a separate verdict for Build, Host tests, Compliance, Smoothness, and Device.
Use `PASS` only for checks actually observed; list `Unverified` items. No commit,
push, flash, or publication is implied by the audit.
