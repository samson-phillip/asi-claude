# 2026-08-17 — Glovebox rebuilt to the design

## Task

Continue the UI polish pass: bring the Glovebox list (screen 31) and the open
document section (14A) to the reference, and apply its assets.

## The list — screen 31

| Element | Reference | Was | Now |
|---|---|---|---|
| Heading | "Digital Glovebox" + one-line subtitle | "Your Glovebox" + a paragraph | Matching |
| Hero | `.gvcard` — gold eyebrow, count, watermark padlock | An `AsiInfoChip` of prose | Card |
| Rows | 32px icon tile, name, status pill, View/Add | Card, emoji tile, "View ›" | Matching |
| Section icons | One glyph per section | **One emoji folder for all four** | Four glyphs |

The icons were the substance. `icon` holds a CloudFront URL for three of the
four sections and the literal string `"globe"` for the fourth; nothing fetches
those, so every section fell back to the same emoji and the four tiles were
indistinguishable. The **code** now picks the glyph, and the admin field is
ignored until an image loader exists to honour it.

## The section — screen 14A

- The "Encrypted · visible to your attorney" line becomes the green pill with a
  lock.
- Document tiles gain the gold-edged thumbnail well, tighter type, and the
  red-tinted remove.
- The upload control becomes the dashed gold "+ Add another document".

**One thing deliberately not copied.** The reference pairs that control with
separate **Camera** and **Gallery** buttons. Nothing in either app captures from
the camera — Android launches `GetContent`, which already offers gallery *and*
files. A Camera button would open the same picker under a false label, so there
is one honest control instead of two until capture is built. Same reasoning that
kept the per-tile delete out while `deleteUserDocument` returned `forbidden`.

## Colour

Gold stands in for the reference's steel blue `#2E78C8` throughout, on the
ruling given today. It is used on every row's icon tile here, not just a link or
two as on Home, so the screen reads noticeably more gold than the mockup — worth
seeing before it is taken as settled.

The remove uses **Live Red**, the palette's single red, as a *tint* rather than a
label colour. It exists for the call screen's on-air badge; this is the only
other place it appears.

## Two faults the render caught that the diff did not

- **The watermark was sizing the card.** Given a plain size it became the tallest
  child and left a band of empty space under the copy. Laid out with
  `matchParentSize` so it cannot.
- **The two counts contradicted each other** — "2 sections on file" and "3 still
  to add" across four sections, because a part-filled section is both. It reads
  "2 of 4 sections on file" and says it once.

## A process fault that cost real work

**I destroyed the signed-in emulator session twice.** `connectedDebugAndroidTest`
uninstalls the app in its teardown, and I was using it to render screens for
screenshots — so every capture run signed the device out. The second time the
session had a real account with three situations saved.

Rendering through an instrumented test is fine on a signed-out device and the
wrong tool on a signed-in one. **Drive the live app for visual checks** unless
the screen is unreachable without state we cannot produce.

Two smaller traps in the same loop: a "non-background pixels" detector matched
the launcher wallpaper, and a "dark background" detector matched a blank navy
screen mid-launch. A useful detector needs both — the app's own background *and*
enough content to prove it drew.

## Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **421 / 421**, 0 failed |

## Next on the polish pass

Done: Home, finish-setup checklist, tab bar, incident tiles, Glovebox list and
section.

Remaining, in the order a member meets them: **Activity** (32), **Profile** (33)
and its sub-screens (33A–33D), the **call** surfaces (28–30A), **notifications**
(24–26), and the **situations picker** (13C).
