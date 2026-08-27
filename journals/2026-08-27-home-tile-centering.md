# 2026-08-27 — Home most-common tiles: centre the content

## Task

On Home, the filled most-common tiles (Test Call, Traffic Stop) had their icon
and text ranged **left**, while the "Add situation" placeholder beside them was
**centred** — so the row read inconsistent. Centre the tile content. Repos:
`kotlin`, `swift`.

## What / why

`IncidentTile` (the Home connect tile, used both for the chosen slots and the
full-list fallback) was a left-aligned `Column`/`VStack`: icon top-left, name and
"Tap to connect" ranged left. The CodePen's home chip (`.gchip`) is
`flex-direction: column; align-items: center` — centred icon over label — and the
`AddSituationSlot` placeholder was already centred. So centring is both what the
reference specifies and what makes the row consistent.

- **Android** — `IncidentTile`: `horizontalAlignment = CenterHorizontally` on the
  Column + `textAlign = TextAlign.Center` on both texts.
- **iOS** — `IncidentTile`: `VStack(alignment: .center)`,
  `.frame(maxWidth: .infinity, alignment: .center)`, `.multilineTextAlignment(.center)`
  on both texts.

Kept the "Tap to connect" subtitle (our affordance; the pen's chip has no
subtitle) — the ask was about alignment, not content.

## Verification

Android — driven on `emulator-5554`: Test Call / Traffic Stop now show the icon,
name, and "Tap to connect" centred, consistent with the Add-situation slot.

| Suite | Result |
|---|---|
| Android — `assembleDebug` (installed + checked on emulator) | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

iOS mirrors the change and builds; not visually driven here (same sim-input
limitation as the recent sheet work).
