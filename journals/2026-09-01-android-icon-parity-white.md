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

## Follow-up: malformed on-device (foreground blown up)

First device glance showed the shield **huge and cropped**. Cause: an adaptive
`<foreground>` is scaled to fill the full 108dp layer, but `ic_launcher_foreground`
was a **58dp layer-list** (intrinsic 58×59) — so the launcher scaled it ~1.9× and
the mask cropped the middle. This was latent in the navy version too; it had never
been looked at on a device.

Fix: `ic_launcher_foreground.xml` is now a real **108×108dp vector** that draws the
shield centred at **scale 0.56** via a `<group translateX=26 translateY=22.36
scaleX/Y=0.56>` (shield ≈56% of the tile, inside the 66dp safe zone). Re-rendered
under circle + squircle masks — centred, no clipping, no blow-up. `assembleDebug`
green.

## Note

Still a **stopgap** on both platforms — the bespoke-icon request to design stands
(`notes/app-launcher-icon-request.md`); when a purpose-built mark arrives it
replaces both the iOS PNG and this adaptive set.

## Files

- `kotlin/app/src/main/res/values/colors.xml`
- `kotlin/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`
- `kotlin/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`
- `kotlin/app/src/main/res/drawable/ic_launcher_foreground.xml`
