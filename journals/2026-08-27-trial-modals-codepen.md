# 2026-08-27 — Trial modals (V2 gate + charge notice) → CodePen

## Task

Match the two trial-conversion modals to the CodePen. Repos: `kotlin`, `swift` —
`feature/trial/TrialSheets.kt` (`GateContent`, `ChargeContent`) and
`Feature/Trial/TrialFlow.swift` (`gate`, `chargeNotice`).

## Changes (both platforms)

**Modal 1 — the trial gate (V2):**
- Header is now a **gold shield badge with "You're on a Trial" inline** beside
  it, at ~22sp (`headlineMedium` / `AsiFont.title`). Dropped the brand wordmark
  lockup, the uppercase "YOU'RE ON A TRIAL" eyebrow, and the oversized "Start your
  membership to connect live" display headline — the reference's modal 1 is just
  badge + title, so the modal is now compact and floats rather than filling the
  sheet.
- Footnote is a **gold-left-barred callout box** (`TrialFootnote` / `trialFootnote`)
  instead of plain centred text.

**Modal 2 — the charge notice (T5/T6):**
- Title dropped from `displayLarge` (32sp) to ~22sp, matching the reference's
  single-line "Start your membership now?".
- Plan card gained a **gold border** (the reference's highlighted plan tile);
  it was a plain filled surface.
- Footnote uses the same gold-left-barred callout.

Shared: one gold-left-bar footnote helper on each platform (3dp `ctaBg` bar,
faint tile, muted text).

## Kept as-is (deliberate)

- The honest copy and behaviour from the trial fix stay: no false "you're
  alerted" promises, `past_due → Pending` handling, etc. Only the visual
  treatment of these two sheets changed.

## Verification

| Suite | Result |
|---|---|
| Android `compileDebugKotlin` | clean; build installed on the emulator |
| iOS `xcodebuild build` | **BUILD SUCCEEDED** |

**No live visual pass:** the modals only appear for a signed-in trial account and
the emulator is signed out (the trial account's session is on the user's device),
so they couldn't be reached on-device here. Compile/build verified.
