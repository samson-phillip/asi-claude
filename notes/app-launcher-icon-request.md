# Request: a purpose-designed app launcher icon (iOS + Android)

**For:** business / design (via Innocent)
**From:** mobile
**Date:** 2026-09-01
**Priority:** low-medium — a stopgap is shipped, but a bespoke icon should replace
it before/around the next store release.

## What we need

A **purpose-designed app icon** delivered as source art plus exported assets, so
both apps show a crafted mark rather than the current stopgap.

Ideally: the **source file** (SVG / AI / Figma, vector) so we can export every size
ourselves. If only rasters are possible, see the exact exports below.

## Why we're asking (context)

The brand shield logo we have (`asi-gold-logo.png`) is drawn with a **white/cream
outer border**, which is designed to frame the mark against a **dark** background.
That makes it a great *in-app* logo on Shield Navy, but a poor *launcher icon*:

- On a **white** tile, the white border disappears and the mark looks unbalanced
  (lopsided edge, washed-out "A").
- On a **navy** tile, it looks premium — but a dark tile reads as almost "black"
  next to other icons and in the App Store Connect build list.

So the logo as-is isn't an icon; it needs a treatment decision and a mark tuned to
fill a square tile. We've shipped a reasonable stopgap in the meantime (below), but
a designer should own the real thing.

### The one design decision to make first

**What is the icon's background — white or navy?** This drives everything, because
the shield's border colour has to change with it:

- **White tile** → the shield needs a coloured (gold or navy) outline, not white,
  or it loses its edge.
- **Navy tile** → the existing white-bordered shield works as-is, but commit to the
  dark tile deliberately.

Our current stopgap chose **white**, matching the previous (v7.x) app's white icon.

## Current stopgap (already shipped, so you can compare)

- A gold two-tone shield with the "A" monogram, **on a white tile**, filling ~76% of
  the square — styled after the previous app's icon but in the new gold palette
  (Justice Gold `#E8A020` / `#C4850A`, cream `#F1E0C1`). The shield's border is gold
  rather than white so it reads on the white tile.
- File: `swift/AttorneyShield/Resources/Media.xcassets/AppIcon.appiconset/AppIcon-1024.png`.
- Android uses a matching adaptive icon (gold shield vector on navy background layer).

## Deliverable spec

**Palette:** the Attorney Shield palette only — Justice Gold `#E8A020` / `#C4850A`,
Shield Navy `#0D1B2E`, creams `#F1E0C1` / `#F6E8CC` (see `design/color-system.md`).

**iOS**
- One **1024×1024 PNG**, sRGB, **flattened — no alpha / transparency** (Apple rejects
  icons with an alpha channel).
- **No rounded corners and no shadow** — iOS applies the rounded-superellipse mask
  itself; deliver a full-bleed square.
- The mark should sit comfortably inside the tile (don't run artwork to the exact
  edge; keep a small safe margin).

**Android (adaptive icon)**
- Foreground and background as **separate** layers on a **108×108 dp** canvas with
  all key artwork inside the central **66 dp safe zone** (launchers mask to circle /
  squircle / rounded-square, and crop outside that).
- Plus a **512×512 PNG** (Play Store listing) and a **monochrome/notification**
  variant if easy.

**Source (preferred):** the vector (SVG/AI/Figma) of the final icon composition, so
we can regenerate any size without re-rasterising.

## Notes

- If the answer is "just use the shield on navy," that's fine — we can wire it in an
  afternoon; we only need a clear yes on the dark tile.
- The in-app logo (`asi-gold-logo.png` on navy) is unaffected by this and stays.
