# Compliance and smoothness checklist

Use this as evidence fields, not a substitute for reading the code. Mark each
row PASS / FAIL / N/A / NOT RUN with the exact command, file, line, or
measurement. A row is not PASS because no obvious problem was seen.

## Compliance

| Check | Evidence to collect |
| --- | --- |
| Repository rules | AGENTS/PROJECT/contribution/security rules read; exceptions recorded |
| Build gate | static and complete gate commands, warnings, exit codes |
| Host tests | names, results, and any skipped tests with reason |
| Changed scope | diff, callers, and shared-contract impact reviewed |
| Memory ownership | allocation/free sites, teardown, null/error paths, bounds |
| Integer/format safety | untrusted lengths and index math; no unsafe format/copy calls without bounds |
| LVGL locking | every cross-task LVGL access locked; no lock held across blocking I/O |
| Task model | stack sizes, priorities, queue/event ownership, watchdog-safe loops |
| Blocking hot path | no flash/network/file/serial wait or long delay in render/input |
| Heap discipline | no per-frame allocation/fragmentation; largest-block risk reviewed |
| Secrets/logging | no credentials/tokens/device secrets in source, logs, captures, or commits |
| Network/TLS | timeouts, certificate policy, error handling, retry bounds |
| Dependencies/licenses | new dependency and third-party notice reviewed |
| Artifacts/config | partition/layout/sdkconfig changes intentional and documented |
| Gate integrity | no disabled tests/warnings, no suppressed failures, no debug leftovers |
| Failure recovery | visible bounded failure; no infinite retry or destructive repair |

## Smoothness

| Measurement | Evidence |
| --- | --- |
| Frame cadence | render/display timings or panel cadence; sample count and scene |
| Dropped/black frames | observed count or probe result |
| Input latency | UP/DOWN/OK short/long/double; missed/duplicate actions |
| Heap | free/minimum and largest block, before/after representative play |
| PSRAM | free/minimum where applicable |
| Stability | watchdog resets, allocation failures, crashes, tearing |
| Thermal/power | only where the feature or board acceptance requires it |

## Verdict

Record Build, Host tests, Compliance, Smoothness, and Device separately. If the
device or a required probe was unavailable, write `NOT RUN` and list the
remaining action. P0/P1 findings block completion and publication.
