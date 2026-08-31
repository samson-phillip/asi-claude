# 2026-08-31 — Trial: "Check again", sheet height, cut-off logo

Three follow-ups from an iOS screenshot of the trial gate sheet.

## 1. "Check again" on the pending screen (both platforms)

The pending screen only offered "Close". Added a **Check again** button that does a
single, immediate entitlement re-read — for a member who wants to know the moment
their `past_due` charge clears rather than waiting on the automatic T7 poll. If
coverage is now live it goes to the confirmed receipt; otherwise it stays pending.

- swift: `TrialViewModel.recheckSettlement()` (spawns) + `performRecheck()`
  (awaitable for tests); button in `TrialFlow.pending`.
- kotlin: `TrialViewModel.recheckSettlement()`; button in
  `TrialSheets.PendingContent`; `onRecheck` threaded through `TrialFlow` and
  wired in `MainActivity`.

The button shows "Checking…" and disables while the read is in flight (reuses the
`converting` flag). Tests on both platforms: from pending, a re-check against a
now-`entitled` account → confirmed.

## 2. Bottom sheet had a large dead space below the content (iOS only)

The custom `FloatingSheet` caps its height at 90% of the screen. `TrialFlow`
wrapped its content in a **`ScrollView`, which greedily expands to that cap** — so
short states like the gate left a big empty area below the footnote (visible in
the screenshot). Dropped the `ScrollView`; the sheet now hugs its content, exactly
like `NudgeSheet` already does. (Kotlin uses a native `ModalBottomSheet`, which
hugs content already — the member confirmed the effect was iOS-only, so no Android
change.) `IncidentTraySheet` keeps its `ScrollView` — it's genuinely tall (a grid
of situation tiles) and needs to scroll, and being tall it never showed dead
space.

## 3. Cut-off logo on the trial gate (iOS only)

The gate's shield badge still used the malformed `brand_shield.png` (the same
clipped "tent" we fixed on Welcome/Home). Switched to `brand_shield_hero` — the
complete vector. (Kotlin's trial gate already used the good `ic_brand_shield`
vector, so no Android change.)

## Files

- swift: `Feature/Trial/TrialFlow.swift` (logo, ScrollView removed, pending
  button), `Feature/Trial/TrialViewModel.swift` (recheck). Test:
  `TrialViewModelTests`.
- kotlin: `feature/trial/TrialSheets.kt` (pending button), `feature/trial/
  TrialViewModel.kt` (recheck), `MainActivity.kt` (wiring). Test:
  `TrialViewModelTest`.

## Test results

- **Android**: full `:app:testDebugUnitTest` — BUILD SUCCESSFUL.
- **iOS**: full `AttorneyShieldTests` — TEST SUCCEEDED.

## Note

The dead-space fix trades the trial sheet's scroll for content-hugging (matching
NudgeSheet). Fine for these bounded states on a normal device; if a future state
grows tall enough to overflow at large Dynamic Type, the proper fix is to move the
scroll+content-measurement into `FloatingSheet` itself. Not needed today.
