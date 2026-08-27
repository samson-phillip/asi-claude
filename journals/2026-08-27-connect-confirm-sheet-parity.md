# 2026-08-27 — Connect confirm sheet (28): eyebrow header + green-check reassurances

## Task

The confirm sheet that appears when you tap a saved most-common tile (screen 28)
didn't match the CodePen. Bring it to parity. Repos: `kotlin`, `swift`.

## Differences found (from the pen's own CSS + the user's screenshot)

1. **Header** — the pen uses a gold uppercase **eyebrow** of the incident
   ("TRAFFIC STOP"), no icon (`.eyebrow{font-weight:800; letter-spacing:.16em;
   uppercase; color:var(--goldhi)}`). Ours showed the incident **icon +
   title-case name** as a row.
2. **Reassurance markers** — the pen uses a **green checkmark in a rounded
   square**: `26×26, border-radius 8, background rgba(46,158,91,.16)` with a
   green tick. Ours used a small green **dot**.

Confirmed both `A licensed attorney…` rows in the pen (tray 27A *and* confirm 28)
use the identical green-square check, so the shared reassurance component can
change once for both.

## Change

- **Header** → gold uppercase eyebrow of `type.name` (Kotlin `labelSmall` +
  `accentText`; iOS `.asiEyebrow(colors)`), matching the tray's eyebrow.
- **`Reassurances`** (shared by 27A + 28) → green tick in a faint-green rounded
  square: `successFill @ 16%` fill, `successFill` tick, 26dp/pt, radius 8. Green
  stays the fill/glyph, never text (color-system R4). Kotlin uses
  `R.drawable.ic_check`; iOS uses the `checkmark` SF Symbol.

Title ("Connect to an attorney now?") and the Connect now / Cancel buttons were
already correct and unchanged.

## Verification

Android — driven on `emulator-5554`: tapping a most-common tile shows the sheet
with the gold "TEST CALL" eyebrow and the two green-square checkmarks. Matches
the reference.

| Suite | Result |
|---|---|
| Android — `assembleDebug` (installed + checked on emulator) | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

iOS mirrors the change and builds; not visually driven here (sim input
limitation).

## Files

- **kotlin** — `feature/home/ConnectSheets.kt` (`ConfirmConnectSheet` header +
  shared `Reassurances`).
- **swift** — `Feature/Home/ConnectSheets.swift` (same).
