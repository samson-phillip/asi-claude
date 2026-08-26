# 2026-08-26 — Situations sheet: square tiles + floating card (emulator-verified)

## Task

Follow-up on the 27B situations picker after a device screenshot: (1) the tiles
must be **square** like the CodePen, and (2) the sheet must **float** (inset card
over the dimmed home) rather than sit edge-anchored. The user granted emulator/
simulator access for visual testing. Repos: `kotlin`, `swift`.

## Fixes

1. **Square tiles.** Restored `aspectRatio(1f)` / `.aspectRatio(1, contentMode:
   .fit)` on the tile; the earlier content-sized version read as short
   rectangles. Icon + label centre in the square.
2. **Floating sheet.**
   - **Android:** Material's `ModalBottomSheet` forces its surface full-width and
     to the bottom edge; a `Modifier.padding` on it does not inset the width
     (confirmed on the emulator — the first attempt was still edge-anchored). Fix:
     make the sheet host transparent (`containerColor = Color.Transparent`,
     `dragHandle = null`, zero content insets) and draw the visible card *inside*
     with `horizontal = 12` + `bottom = 12` margins, all corners rounded (26dp), a
     1px hairline border, and a hand-drawn grab handle. The scrim and slide-up
     stay the sheet's.
   - **iOS:** SwiftUI `.sheet` also anchors edge-to-edge, and a
     `fullScreenCover` detaches the presenter (would show black, not the dimmed
     home). Fix: a **root-ZStack overlay** (sibling of the tour overlay) — a
     full-screen scrim with the whole app (content + tab bar) dimmed behind it,
     and an inset rounded card floating above the bottom. Scrim fades, card
     slides up (`withAnimation` + transitions).

## Verification

Android — driven on `emulator-5554` (Pixel, API shown) via adb, full flow:

| Step | Result |
|---|---|
| Open sheet from Home "Choose" | Floats: inset card, rounded all corners, hairline, grab handle, dimmed home + gap above nav bar ✓ |
| Tiles | Square, icon-over-label ✓ |
| Select two | Brighter gold border + gold-tint fill + gold glow + gold check ✓ |
| Done | Saved, sheet dismissed, Home refreshed in place — "YOUR MOST COMMON SITUATIONS" showed the two picks + an "Add situation" slot; readiness 62%→75% ✓ |

| Suite | Result |
|---|---|
| Android — `assembleDebug` | **BUILD SUCCESSFUL** (installed + driven on emulator) |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

**iOS visual check not done.** The simulator's framebuffer is capturable
(`simctl io screenshot`) but I could not send *input* to sign in and navigate:
no `idb`, and `cliclick`/`osascript`/`screencapture` are all blocked by macOS
accessibility + screen-recording permissions that can't be granted
non-interactively here. The iOS layout was therefore chosen for robustness (root
overlay = app guaranteed behind, no cover-detach risk) and mirrors the
emulator-verified Android result. Worth a manual eyeball, or grant this
environment Accessibility + Screen Recording and I can drive it.

## Files

- **kotlin** — `feature/situations/SituationsScreen.kt` (square tile),
  `feature/situations/SituationsSheet.kt` (transparent-host floating card).
- **swift** — `Feature/Situations/SituationsScreen.swift` (square tile),
  `Feature/Situations/SituationsSheet.swift` (floating overlay: scrim + inset
  card + transitions), `AttorneyShieldApp.swift` (root-ZStack overlay; removed the
  `.sheet`; `onEditSituations` animates in).

## Note — other sheets

The user observed "the bottom sheets" (plural) don't float. Only 27B is floated
so far. If they want it everywhere, the same treatment should roll out to the
connect tray (27A), confirm (28), and nudge (25). Deferred pending confirmation —
a shared floating-sheet wrapper would keep it consistent.
