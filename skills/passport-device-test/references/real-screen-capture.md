# Capture the real firmware screen

Use a framebuffer capture of the running firmware as the default visual evidence.
A mockup, source review, emulator window, or phone photo is not a substitute for
the pixels the panel actually received.

## Preconditions

- The device is connected over a data-capable USB cable, the port is identified,
  and the user has authorized observation. Capturing is read-only; it must not
  reboot, erase, flash, or change settings.
- The firmware implements the publisher's `FAP_SCREENSHOT_V1` protocol, or the
  project has an equivalent read-only framebuffer capture path. If it does not,
  add the protocol only as an authorized implementation change; otherwise mark
  visual verification `NOT RUN`.
- Serial console logging is quiet during the binary payload; any log byte in the
  declared payload corrupts the image.

## Capture with the official publisher

Prefer the installed `folotoy-ai-passport-publisher` skill's `capture-screen`
command. It writes the PNG and an adjacent `.fap-capture.json` receipt with the
hash, dimensions, port, protocol, and capture time.

```bash
capture-screen --list-ports
capture-screen --port <PORT> --output docs/evidence/<candidate>-screen.png
```

If the standalone command is not on `PATH`, call the publisher script directly:

```bash
python3 <publisher-skill>/scripts/publisher.py capture-screen --list-ports
python3 <publisher-skill>/scripts/publisher.py capture-screen --port <PORT> --output <PNG>
```

On Windows use `py -3` and the publisher script's Windows path. Do not guess the
port from an arbitrary device; resolve multiple or uncertain devices with the
user. Keep the capture command's stderr and receipt; do not fabricate a receipt.

## Protocol and validation

The host sends the ASCII line `FAP_SCREENSHOT_V1\n`. The device replies with one
header and exactly the declared payload:

```text
FAP_SCREENSHOT_V1 <width> <height> RGB565LE|PNG <byte_length>\n
<payload>
```

`RGB565LE` length must equal `width * height * 2`; `PNG` must be a complete PNG
with matching dimensions. Validate the saved file:

- dimensions from the PNG and receipt match the device header;
- the receipt hash matches the PNG;
- open the actual PNG with `read_image` and inspect it;
- the file contains no device secrets, credentials, tokens, or personal data
  before it is committed or attached to a public submission.

## Compare and correct

Capture every changed screen and state, not only the first frame. Check title,
text/glyphs, layout, contrast, HUD, button hints, and failure/placeholder states
against the intended design and the accepted reference. When they differ, fix the
firmware, rebuild/reinstall, and capture again; do not edit the screenshot to make
the check pass. Keep the final image and receipt with the candidate record.

## Limits

A screenshot proves static pixels only. It cannot prove animation continuity,
input latency, audio, RF, thermal behavior, or sustained smoothness. Use the
device measurement plan in `passport-code-audit` and the project acceptance guide
for those facts. If the port, protocol, authorization, or fresh capture is
unavailable, report `NOT RUN` and the remaining action; never call a simulator,
mockup, or stale image a real capture.
