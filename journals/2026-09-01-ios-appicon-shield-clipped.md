# 2026-09-01 — iOS app icon: shield clipped at the bottom

## Symptom

On the iOS home screen the AttorneyShield launcher icon showed the gold shield
with its **bottom point cut off** (flat) and sitting high in the tile.

## Cause

The old `AppIcon-1024.png` had been composited from
`brand_shield.imageset/brand_shield.png` — a **bad raster export**: the shield in
that PNG is itself clipped flat at the bottom (no point), only fills the top half
of its 300×342 canvas, and carries stray cyan artifacts. Compositing it produced
a high, bottom-clipped mark.

## Fix

Rebuilt the icon from the **clean vector** source
(`brand_shield_hero.imageset/brand_shield_hero.svg`) — the same heraldic shield
the app draws, with a proper point and the "A" monogram, in-palette (Justice Gold
`#E8A020`/`#C4850A`, cream `#F1E0C1`, Shield Navy ground `#0D1B2E`).

Because no SVG rasteriser is installed (no rsvg/cairosvg/inkscape), composed a
self-contained square SVG — a full 1024×1024 navy `<rect>` plus the shield nested
and scaled to **~60% height, centred** (`preserveAspectRatio="xMidYMid meet"`) —
and rasterised it with `qlmanage` (QuickLook). The full-canvas navy rect avoids
QuickLook's white-background quirk. Then flattened RGBA→RGB with PIL so the icon
carries **no alpha** (Apple requirement). Result: shield fully visible, even
margins, point intact.

## Android

Checked for parity — **not affected**. The Android adaptive icon's foreground is
the clean `ic_brand_shield` **vector** (viewport 100, proper shield), sized 52×59dp
centred inside the 108dp foreground, which sits within the adaptive safe zone — no
mask clipping. No change needed.

## Verify

- iOS build **SUCCEEDED** (AppIcon compiled, no alpha warning).
- On device/simulator the icon may be **cached**: delete the app and reinstall (or
  erase the simulator's home screen cache) to see the new mark.

## Files

- `swift/AttorneyShield/Resources/Media.xcassets/AppIcon.appiconset/AppIcon-1024.png`
  (regenerated from the vector; the only changed file).
