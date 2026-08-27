# 2026-08-27 — Home shield: make the breathing glow read as a pulse

## Task

The CodePen guardian shield has a gold glow that fades in and out — breathing
with the rings. Ours technically had it (`.gaura`) but it was too subtle to
notice; the user asked to bring the effect out. Repos: `kotlin`, `swift`.

## Why it wasn't reading

The aura was present (radial gold gradient, scale + opacity animated on the same
2.4s cycle as the rings), but three things kept it invisible:

1. The 88dp shield sits over the aura's bright centre, so only a halo could
   show — and the glow only reached ~17dp past the mark (170dp bloom, transparent
   at 72%).
2. The opacity swing was narrow (`.55 -> 1`), so it read as a static wash rather
   than a pulse.
3. The centre gold was `.38` alpha — faint once occluded.

## Change

Enlarged and strengthened the bloom so a gold halo visibly pulses around the
shield, in step with the rings:

- Bloom `170 -> 186dp`, gradient extended (`transparent` at `.80` not `.72`,
  iOS `endRadius 85 -> 93`).
- Centre gold `.38 -> .50`, mid-stop `.14 -> .20`.
- Opacity swing widened `.55->1` → `.35 -> 1`; scale `.88->1.1` → `.86->1.1`.

Still `AsiPalette.ActiveGold` (#E8A020) — the pen's home variant uses a lighter
`#F7D046`, which is outside our palette, so we keep Active Gold.

## Verification

Android — captured two Home frames ~2s apart on `emulator-5554`: one with the
bloom expanded/bright and larger rings, one dim/contracted — i.e. the glow now
visibly breathes.

| Suite | Result |
|---|---|
| Android — `assembleDebug` (installed + checked across the breath cycle) | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

iOS mirrors the same values and builds; not visually driven here (sim input
limitation).

## Files

- **kotlin** — `feature/home/HomeScreen.kt` (`ShieldHero` aura).
- **swift** — `Feature/Home/HomeScreen.swift` (`ShieldHero` aura).
