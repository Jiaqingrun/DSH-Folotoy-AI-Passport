# First-upload cover render

Use this only for a **new** play (no `--project-id`). Updates preserve the
published cover unless the user explicitly asks for a replacement.

## Required result

- Portrait **3:4**, preferably `1152x1536`; PNG, JPEG, or WebP; <= 10 MiB.
- A finished render of the actual app/game: its world, action, characters, or
  core interaction. It must read as this play, not a generic AI Passport photo.
- If the device appears, keep the real shell, buttons, ports, key-ring hole,
  logo, and colorway. Do not invent hardware. The screen must show plausible
  gameplay, never black, dim, blank, or a loading/error UI.
- No placeholder, watermark, store screenshot, or unrelated asset. Generated
  artwork is an illustration, not a real screenshot.

## Generation prompt template

Adapt the bracketed parts from the project and conversation:

```text
Create a portrait 3:4 community cover illustration for the AI Passport game
"[name]". Show [the core scene / action / characters / interaction], with
[palette and mood]. Compose for a small portrait thumbnail with one clear focal
point and readable shapes. [If a device is included: use the attached AI
Passport front reference as the exact shell base; keep its outer hardware,
buttons, ports, key-ring hole, logo, and colorway unchanged; redraw only the
screen area with the game's actual UI.] No added text, logos, watermarks, or
interface chrome beyond the device's real shell labels and the game screen; no
invented hardware. Finished artwork, not a loading screen or placeholder.
```

## Verification

1. Wait for explicit generation completion; a task id, preview URL, or HTTP 200
   is not completion.
2. Open the exact local upload file with `read_image`.
3. Confirm 3:4, finished content, plausible screen, no secrets/personal data,
   no unintended text, and no invented hardware.
4. If it is unfinished or wrong, regenerate or use a suitable finished project
   image. If neither is possible, stop and ask the user; never upload a
   placeholder with a plan to fix it later.
