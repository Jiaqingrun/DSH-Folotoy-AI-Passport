---
name: passport-publish
description: Prepare, validate, and submit a FoloToy AI Passport firmware update or new play through the official publisher CLI. Use only after passport-router produced a card and the user approved the exact target. Never handle authorization codes or tokens.
whenToUse: The user says publish, submit, update the store, or asks to prepare release copy for an existing AI Passport play.
---

# Publish an AI Passport project

## Preconditions

1. A `passport-router` card exists and the class is A or B. Class C: stop.
2. The official `folotoy-ai-passport-publisher` skill is installed. If not, stop and ask the user to install it from the official release. Do not copy it into this bundle.
3. The user authorized the publisher CLI manually. Never ask for, read, store, echo, or log a code/token.
4. The target is an update of an existing play (for example 1943 or 2170) unless the user explicitly asks for a new play. Both known plays are already published; a new submission is a new revision, not a second play.

## Cover policy (default)

- **First upload (no `--project-id`):** generate a portrait 3:4 render of the
  actual finished app/game as the cover. Prefer 1152x1536. Make it gameplay-first:
  show the play's world, action, characters, or core interaction. A device may
  appear, but use its real shell/buttons/ports and never add hardware that does
  not exist. A generic device photo, a placeholder, a loading/error page, or an
  unrelated image is not acceptable. Open the exact file that will be uploaded.
  If no image renderer is available or the render is unfinished, stop and ask
  the user; do not upload without a finished cover. See
  [`references/cover-render.md`](references/cover-render.md) for the required
  result, prompt template, and visual verification.
- **Update (`--project-id`):** preserve the currently published cover by default.
  Do not regenerate or restyle it. Omit `--cover`; `publish.py` finds the exact
  3:4 cover under `--root` (or uses `--previous-cover`) and reuses that file.
  The publisher still needs a complete revision, so pass the same cover bytes;
  the cover remains visually unchanged. Replace the cover only when the user
  explicitly asks, then pass the new `--cover`.
- **Automatic update (`--auto`):** the same preserve rule applies. A one-time
  update grant authorizes the upload; it does not authorize a new cover.

## Steps

1. Confirm the exact target: play id, firmware path, cover path, zh/en title,
   instructions, changelog. For a new play the cover must be a generated render;
   for an update the default is the existing published cover. The user-facing
   instructions must document what all three function buttons do, including
   relevant long-press actions; never describe a dead or unused button.
2. Run the preflight with the project root, firmware, cover that will be
   uploaded (`--root` plus the preserved cover for updates), and publisher path:
   - macOS/Linux: `<base>/scripts/preflight.sh ...` or `python3 <base>/scripts/preflight.py ...`
   - Windows: `<base>\scripts\preflight.cmd ...` (works under the default execution policy),
     or `py -3 <base>\scripts\preflight.py ...`. `preflight.ps1` only runs with
     `-ExecutionPolicy Bypass`.
   Fix every FAIL before continuing.
3. Run the official validator:
   - macOS/Linux: `python3 <publisher>/scripts/publisher.py validate --kind firmware --firmware <fw> --cover <cover>`
   - Windows: `py -3 <publisher>\scripts\publisher.py validate --kind firmware --firmware <fw> --cover <cover>`
4. Open the cover with `read_image`. Check exact 3:4, readable text, no watermark, no store screenshot, no AI-generated placeholder. The validator does not check content.
5. Run `<base>/scripts/lint_store_copy.py` on the zh/en instructions and changelog; add `--require-changelog` when updating. Use `python3` on macOS/Linux or `py -3` on Windows. Fix length/placeholder failures.
6. Run the dry-run and show the exact command to the user:
   - New upload: pass `--cover <generated-render>`; the wrapper refuses to
     continue without a cover and tells you to generate one.
   - Update: omit `--cover` and pass `--root <project-root>`; the wrapper prints
     the preserved cover it will reuse. Use `--previous-cover <path>` when the
     cover is outside the project root. Pass a new `--cover` only when the user
     explicitly requested a cover change.
   - macOS/Linux: `<base>/scripts/publish.sh --dry-run ...` or `python3 <base>/scripts/publish.py --dry-run ...`
   - Windows: `<base>\scripts\publish.cmd --dry-run ...` or
     `py -3 <base>\scripts\publish.py --dry-run ...`
7. Only after the user explicitly confirms, run the same script with `--execute --confirmed ...`. `--confirmed` alone only prints the command; it does not upload. It never passes `--auto`.
8. Save the receipt JSON. Report play id, revision, updatedAt, and firmware sha256. Without a receipt, say "提交未确认成功", not "已发布".

## Store rules (quick reference)

- Firmware ≤ 8 MiB; cover exactly 3:4, ≤ 10 MiB; up to 4 extra 3:4 images.
- Instructions ≤ 8000 characters per language; changelog ≤ 4000; Chinese instructions required; Chinese changelog required on update.
- `--tag` is parsed but not sent by `submit`; server AI assigns category/tags. `--category` only matters for print.
- Device token has no create/update scope; `--auto` needs a `create_once`/`update_once` grant. This bundle does not automate that grant.
