# 2026-08-26 — Float every sheet via a shared FloatingSheet wrapper

## Task

After 27B (situations) was floated, the user asked to roll the floating treatment
out to the other bottom sheets so they read consistently: the connect tray
(27A), the connect confirmation (28), the gentle nudge (25), and — for full
consistency — the trial gate (B2). Repos: `kotlin`, `swift`.

## Approach — one shared wrapper per platform

Rather than duplicate the float trick at each call site, the treatment lives in
one place per platform and every sheet routes through it.

- **Android** — `core/design/FloatingSheet.kt`: a `ModalBottomSheet` with a
  transparent container (`Color.Transparent`, `dragHandle = null`, zero content
  insets) and an inset rounded card drawn inside (side + bottom margins, 26dp
  corners, 1px hairline, own grab handle). Material forces its surface full-width
  and to the bottom edge, so the transparent-host-plus-inset-card is the only way
  to lift it off the edges while keeping the scrim, slide-up, and swipe.
  `SituationsSheet`, `IncidentTraySheet`, `ConfirmConnectSheet`, `NudgeSheet`, and
  `TrialFlow` all now call `FloatingSheet { ... }`.
- **iOS** — `Core/Design/FloatingSheet.swift`: a root-overlay card (full-screen
  scrim with the app dimmed behind, inset rounded card with a grab handle, scrim
  fades / card slides). `.sheet` anchors edge-to-edge and `fullScreenCover`
  detaches the presenter, so the sheets are presented from the **root ZStack**
  (beside the tour overlay) as `if <flag> { FloatingSheet { Content } }`, which
  guarantees content + tab bar render behind. The content views dropped their own
  background / `presentationDetents` / `interactiveDismissDisabled` and trimmed
  their top padding for the handle.

## Behaviour preserved

- Trial **Processing (T7)** stays non-dismissible — the scrim's `onDismiss`
  no-ops on that step (Android: the step-based `onDismiss` lambda; iOS: a
  `guard trial.step != .processing`).
- The **nudge precedence guard** is intact: it only shows when nothing louder is
  up (tray / confirm / trial / situations) and not during the tour.
- `begin(type)` still clears `tray`/`confirming` before navigating to the call.

## Verification

Android — driven on `emulator-5554`, screenshots confirm the float:

| Sheet | Result |
|---|---|
| Situations (27B) | Floats — inset card, square tiles, soft glow ✓ (earlier) |
| Connect tray (27A) | Floats — inset card, rounded corners, hairline, handle, shield peeking above ✓ |
| Confirm (28) | Floats — inset card, dimmed home behind ✓ |
| Nudge (25) / Trial (B2) | Same shared wrapper → float identically |

| Suite | Result |
|---|---|
| Android — `assembleDebug` (installed + driven) | **BUILD SUCCESSFUL** |
| Android — `testDebugUnitTest` | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

Fixed one iOS compile error along the way: a `$0` inside a nested
`withAnimation` closure in `onTileTapped` broke the outer closure's argument
inference — named the parameter (`type in`) instead.

**iOS visual check still pending** — the simulator can't be UI-driven in this
environment (no `idb`; `cliclick`/`osascript`/`screencapture` blocked by macOS
Accessibility + Screen-Recording perms that can't be granted non-interactively).
The iOS rollout mirrors the emulator-verified Android result and reuses the
already-working 27B root-overlay pattern, so risk is contained — but a manual
eyeball (or granting this environment those perms) would close the loop.

## Files

- **kotlin** — new `core/design/FloatingSheet.kt`; refactored
  `feature/situations/SituationsSheet.kt`, `feature/home/ConnectSheets.kt`,
  `feature/notifications/NudgeSheet.kt`, `feature/trial/TrialSheets.kt`.
- **swift** — new `Core/Design/FloatingSheet.swift`; refactored
  `Feature/Situations/SituationsSheet.swift`, `Feature/Home/ConnectSheets.swift`,
  `Feature/Notifications/NudgeSheet.swift`, `Feature/Trial/TrialFlow.swift`, and
  `AttorneyShieldApp.swift` (removed the four `.sheet`s → root-ZStack overlays).
