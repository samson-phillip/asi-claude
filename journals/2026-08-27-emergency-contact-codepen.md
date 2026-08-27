# 2026-08-27 — Add-emergency-contact screen → CodePen (screen 16)

## Task

Match the "Add an emergency contact" screen to the CodePen design. Repos:
`kotlin`, `swift` — the form lives in `ProfileCompletionScreen` (`ContactPane` /
`contactPane`).

## Changes (both platforms)

- **Gold eyebrow "EMERGENCY CONTACTS"** above the title — the reference's header
  treatment, was missing.
- **Reordered "Notify them by" above "Relationship"** — CodePen order.
- **"Notify them by" → green check tiles** (`NotifyChip`): a green rounded square
  with a white tick when on (white on Verified Green, 5.34:1 — allowed), an empty
  bordered square when off, label beside it, laid side by side. Replaces the
  vertical plain checkboxes. Hint "Choose one or both …".
- Relationship pills unchanged (`AsiChoiceChips` already renders the selected pill
  in gold).

## Deliberate divergences from the CodePen (flagged to the user)

These are the app's existing, principled choices — kept, not reverted:

1. **Subtitle** stays "Who an attorney should know about, and how to reach them",
   NOT the CodePen's "They're alerted with your location the moment you connect."
   Nothing sends that alert (backend confirmed; `notifyBySms` schema says so). A
   member must not leave believing someone will be told.
2. **Notify hint** keeps an honesty clause ("Saved for when alerts are switched
   on — nothing is sent yet") rather than the bare "Choose one or both".
3. **Notify tiles are not pre-checked** (CodePen shows both green/checked) — the
   gateway defaults both false for consent hygiene: an unset field must not stand
   in for consent to contact a third party. They also stay disabled until the
   matching phone/email field has a value.

## Not changed (app-convention vs one-screen fidelity — flagged)

- Fields keep the app's floating-label `AsiTextField` (CodePen puts bold labels
  *above* each field). Phone stays a Code + Mobile pair (CodePen is one field with
  an inline `+1`). Changing these means either diverging this one screen from the
  app's shared field component or reworking it app-wide — left for a decision.
- The completion-flow brand/Back chrome stays (CodePen is chrome-less).

## Verification

| Suite | Result |
|---|---|
| Android `testDebugUnitTest` | green; `compileDebugKotlin` clean; build installed |
| iOS `xcodebuild build` + `ScreenRenderTests` | **BUILD/TEST SUCCEEDED** (the pane renders) |

**No live visual pass:** the screen sits inside the auth-gated setup flow and the
emulator is signed out (session is on the user's device), so it could not be
reached on-device here. Logic/render verified; on-device check pending a session.

## Files

- `kotlin` — `feature/profile/ProfileCompletionScreen.kt` (eyebrow, reorder,
  `NotifyChip`).
- `swift` — `Feature/Profile/ProfileCompletionScreen.swift` (same).
