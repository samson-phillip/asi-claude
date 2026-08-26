# 2026-08-26 — Account to the CodePen: open-seat card, footnote, hub cleanup

## Task

Bring the Account area to visual parity with the CodePen "V6" reference. Account
is a multi-pane screen (hub → Profile / Payment & plan / Family / Settings), so
the parity work spans several panes. Repos: `kotlin`, `swift`.

The 33D inline-edit for the Payment Method card (Expiration + Billing ZIP + Save,
backed by the now-shipped `updatePaymentMethod`) landed in an earlier commit this
push; this entry covers the remaining Account panes.

## Changes

1. **Family pane — reveal-form behind a dashed "open seat" card.**
   The reference doesn't show an always-open add-member form; it shows an empty
   "open seat" placeholder (dashed border) that reveals the form when tapped, with
   a footer explaining seat allocation. Rebuilt `FamilyPane` around an
   `OpenSeatCard` (`Modifier.dashedBorder` on Kotlin, `RoundedRectangle`
   `.strokeBorder` with a dashed `StrokeStyle` on Swift) + a reveal-form (VM state
   `addFormOpen`, `openAddMember`/`cancelAddMember`; success resets it) + footer.
   Dropped the form's own heading and the redundant seat-count line, added a
   Cancel action.
2. **Sub-account guards.** Plan and Membership panes (and the corresponding hub
   rows) are guarded for sub-accounts — a family member on someone else's plan
   shouldn't see plan-management controls. `isSubaccount` getter on the VM.
3. **Hub cleanup.** Removed the redundant email line from the account hub; it's
   already shown on the Profile pane.
4. **Settings footnote.** Added the reference's footnote pointing to where the
   Delete-account action actually lives ("Delete account lives in Payment &
   plan."), rather than a dead Delete row in Settings.

## Decisions

- **Honest actions over CodePen chrome.** The dashed open-seat card matches the
  reference visually, but the form behind it uses the real `addFamilyMember`
  path — no fabricated seat state. Same principle applied throughout this push.
- **No dead Delete row.** The reference's Settings pane hints at deletion; rather
  than add a control we can't yet wire, the footnote points to where it lives.

## API endpoints used

- `addFamilyMember` (Family pane reveal-form submit) — existing.
- `updatePaymentMethod` (33D inline-edit, earlier commit this push) — the A2 item
  the backend shipped.

## Verification

| Suite | Result |
|---|---|
| Android — `testDebugUnitTest` | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

## Next

- **Activity** — drop the transcript (backend A1: dropped/not recommended), add
  outcome labels via `commsCallsByMember` (port `callOutcome`).
- **Notifications** — split the merged centre/settings view.
- Deferred: Account hub-row reorg (needs "PIN & security" and
  "Support & intro video" screens); Settings "Language" row (needs a switcher);
  Glovebox masking (backend A3 sensitive-field flag) + per-section watermarks.
