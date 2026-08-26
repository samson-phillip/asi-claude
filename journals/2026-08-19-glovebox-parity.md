# 2026-08-19 — Glovebox section detail to the CodePen (14A–14D)

## Task

Bring the Glovebox to CodePen parity. Repos: `kotlin`, `swift`, this one.

## What the audit wanted, and what member-client actually does

The audit's headline: the section detail is an **always-editable form showing raw
PII**, where the CodePen (14A) shows a **calm masked read-only view with one Edit
action**. Two distinct things — read-only-with-Edit, and masking.

Checked `member-client` before building: it **does not mask** document values
(masking exists only for phone/email in verification), and it renders sections as
**always-editable forms** — the same as our app. So the CodePen's treatment is a
*look* that neither the reference behaviour nor the schema supports out of the box.

## Shipped

- **Read-only section view + an Edit action.** A section now opens read-only: text
  and dropdown fields render as label-over-value rows ("Not set" when empty). An
  **Edit** button flips them to inputs; **Save changes** commits and returns to the
  read-only view; **Cancel** discards. Files can be added/opened either way (the
  reference manages files independently of the text Edit). A section that is only
  files shows no Edit button (nothing to edit). New VM state: `isEditing`, with
  `startEditing` / `cancelEditing`, reset on open/back and cleared on save.
- **Encryption pill is text-only** now (dropped the lock icon we'd added; the
  reference pill carries no glyph). Still a Verified-Green *fill*, never green text
  (R4).

## Deliberately not done (blocked)

- **Masking sensitive values.** The read-only view ships **unmasked** because the
  schema has no way to say *which* fields are sensitive — `DocumentField.kind` is
  only text/dropdown/file, and member-client doesn't mask. Masking "License number"
  but not "State" needs a backend **`sensitive` flag** on the field. Raised as **A3**
  in [[backend-asks-codepen-parity]].
- **Per-section watermarks.** The reference marks each section with its own faded
  motif (shield / cross-and-pulse / rings / globe-and-stamp); the app draws one
  generic shield for all four. This needs **four distinct illustration assets** —
  a design-art follow-up, not a code change. Left as the single shield for now.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — build | **BUILD SUCCEEDED** |

Not eyeballed on-device (the emulator is signed out); the read-only↔edit toggle is
straightforward to verify on a device with a seeded document section.

## Next parity screens

Account (Family dashed spot-cards, Settings pane, hub email), Home (remove the
non-design extras, heading/link, grace state — keeping the 2-col tiles),
Notifications (split centre/settings), Activity ("Practice run").