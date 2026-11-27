---
name: passport-device-test
description: Guide authorized flashing and on-device acceptance of FoloToy AI Passport firmware, including device discovery and bounded serial observation. Use for explicit device-test or flash requests, not merely because a build succeeded.
---

<p align="right"><a href="SKILL.zh_CN.md">简体中文</a> · <strong>English</strong></p>

# Flash and Test on the Device

Locate the user's checkout; read `AGENTS.md`, the on-device handoff in
`docs/development/ai-guide.md`, and the flashing/data policy in
`docs/development/engineering/firmware-layout.md`. Use the applicable hardware
acceptance checklist, not every peripheral test for every change.

## Establish access, artifact, and consent

1. Discover ports read-only with the platform's enumeration tools; an activated
   IDF Python can use `python -m serial.tools.list_ports -v`. Do not open/reset
   arbitrary ports or assume the first port is the target. Resolve multiple or
   uncertain devices with the user.
2. If no device is detected, ask the user to turn it on and connect it to a
   computer USB port with a data-capable cable, then recheck after confirmation.
   In a remote/VM/WSL environment without access, say access is unavailable, not
   that the physical device is disconnected. Provide local steps if necessary.
3. Bind the target device to an exact verified firmware and the user's data
   requirements. For a gate-produced bundle run
   `python3 tools/archive_firmware.py verify <archive-directory>` (or
   `py -3 tools\archive_firmware.py verify <archive-directory>` on Windows) and compare
   the chosen image hash with its manifest. For other builds require equivalent
   target/layout evidence; do not assume any `.bin` is a merged image.
4. Confirm the specific port, firmware, intended write range/data impact, and
   consent for this flash before writing. Existing explicit consent covering
   those facts need not be asked again. A build request, earlier-version
   approval, connected device, or publishing approval alone is insufficient.

## Flash only the intended data

For an approved complete refresh, flash the verified merged image from `0x0`
using the activated toolchain and the confirmed port. Check the installed
esptool's help for command spelling/options. An application-only binary never
belongs at `0x0`.

If settings must survive, do not write the merged image blindly: confirm a
compatible partition layout and use verified component images at their actual
configured offsets. If that evidence or the matching components are missing,
stop and obtain them. Do not run a rebuild-and-flash command that silently
changes the artifact just approved. Treat `flash_args` as data, never execute it
as a shell script. Whole-chip erase is a separate destructive choice, not a
default repair. Backing up the original firmware is not a prerequisite.

On connection/write failure, capture the error and check access, port ownership,
cable, and boot state. Retry only after a relevant correction and within the
approved target/scope. Do not cycle indefinitely, kill unrelated processes,
change system permissions, or erase Flash without new authorization.

## Capture the real screen before judging UI

After the approved firmware boots, capture the running framebuffer as the
default visual evidence. Use the installed publisher's `capture-screen` command
or the project's equivalent read-only `FAP_SCREENSHOT_V1` path; see
[`references/real-screen-capture.md`](references/real-screen-capture.md). Save
the PNG plus its `.fap-capture.json` receipt, verify the dimensions and hash,
and open the actual PNG with `read_image`.

Compare each changed screen and state with the intended design and accepted
reference. Check title, text/glyphs, layout, contrast, HUD, button hints, and
failure states; fix the firmware and recapture when they differ. Do not edit the
screenshot, and never present a mockup, source tree, emulator window, phone
photo, or stale image as a real capture. If the port, protocol, authorization,
or fresh capture is unavailable, mark visual verification `NOT RUN` and state
the remaining action. A capture proves static pixels only; it does not prove
animation comfort or sustained smoothness.

## Observe and record

After approved flashing, collect a bounded startup-log window with the matching
ELF available for decoding; explain if opening a monitor will reset the device.
Ask the user to exercise the changed behavior and report visible/audible results.
Record the image identity, test actions, outcomes, and failure reproduction.
Stop the monitor before handing back the port. Keep raw logs local and sanitize
secrets before sharing. Route crashes to `passport-debug` if available.

Flashing success, clean logs, and a fresh capture do not prove audio quality,
button behavior, RF performance, sleep current, or sustained smoothness. Whenever the input changed,
exercise all three function buttons (UP/DOWN/OK) including every documented
short, long, and double action, and compare each on-screen hint with the real
key. Confirm no function key is dead, duplicated, arbitrary, or misleading; a
button map that exists only in source is not acceptance. Report `Build`,
`Host tests`, `Device tests`, and `Unverified` separately, limiting PASS to
checks actually observed. If declined or inaccessible, mark device testing NOT
RUN and hand off the pending steps. No commit, push, or publication is implied.
