# 2026-09-01 — Android launcher icon: match the iOS white-tile icon

Follow-up to the iOS icon work: Android still had the **navy** adaptive icon and
none of the iOS iterations had been mirrored. Brought it to parity.

## Changes (`kotlin`)

- `res/values/colors.xml` — added `asi_icon_bg = #FFFFFF` (kept separate from
  `asi_bg_primary` so the app's navy window background is untouched).
- `res/mipmap-anydpi-v26/ic_launcher.xml` + `ic_launcher_round.xml` — adaptive
  **background** `@color/asi_bg_primary` (navy) → `@color/asi_icon_bg` (white).
- `res/drawable/ic_launcher_foreground.xml` — widened the shield box **52dp → 58dp**
  (~+12%) to echo the iOS icon's wider mark, keeping height 59dp so every corner
  stays inside the 66dp adaptive safe zone (verified against circle + squircle
  masks — no clipping).

The foreground vector (`ic_brand_shield`) is the same official shield mark iOS
uses, so on the white background it reads identically — including the same subtle
right-rim asymmetry (the shield's white outer edge reads as the tile), accepted on
iOS too.

## Verify

- `:app:assembleDebug` **BUILD SUCCESSFUL**.
- Rendered the adaptive icon under squircle + circle masks: white tile, centred
  widened gold shield, no clipping.

## Note

Still a **stopgap** on both platforms — the bespoke-icon request to design stands
(`notes/app-launcher-icon-request.md`); when a purpose-built mark arrives it
replaces both the iOS PNG and this adaptive set.

## Files

- `kotlin/app/src/main/res/values/colors.xml`
- `kotlin/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`
- `kotlin/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`
- `kotlin/app/src/main/res/drawable/ic_launcher_foreground.xml`
