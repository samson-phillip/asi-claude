# 2026-08-31 — In-app phone capture (Stage 4 screens 08/09, on demand)

## Task

Follow-up to the Stage-4 discussion. The member spotted the real hole: web
registration makes the phone **optional** (`member-client`'s PublicCheckoutScreen
labels it "Phone (optional)" and submits nothing when blank), and the app had no
in-app way to capture it — screens 08 (phone entry) and 09 (verify) were built
but unreachable. A phone-less web registrant would lose the number entirely.

Chosen scope (member-approved): surface it **only when the phone is missing**
(`phoneE164 == nil`), as a Stage-5 checklist row that opens the existing 08/09
panes. No new screens, no new endpoints.

## What shipped (both platforms)

- **`ProfileStep.phone`** added; `loadProfileReadiness` fetches `getMe` once and
  adds an "Add your phone number" task **only when it can prove the phone is
  absent** (read succeeded and `phoneE164 == nil`). An unreadable `getMe` is
  never treated as missing (the loader's existing rule), so a network hiccup
  never nags. Members who have a number get no row and no percentage change.
- **Routing**: the checklist row (and the notification-centre setup row) route
  `.phone → openSetupAt(.phone)`.
- **Setup wizard, phone-only mode**: a run started at `.phone` from the checklist
  is scoped to just `[phone, verifyPhone]` (`phoneOnly` flag) and returns to the
  checklist after verifying, rather than marching the member on through
  details/address/PIN they already did. Also: the "already complete" bounce now
  only fires for auto-entry (`startAt == nil`) — an explicit phone request is
  honoured even though phone isn't part of that "complete" check.
- Exhaustive `when`/`switch` over `ProfileStep` (the nudge title/body copy)
  gained a `.phone` branch. Phone is deliberately **not** in the nudge priority
  list — it's a checklist row, not a nudge.

## Files

- kotlin: `core/profile/ProfileReadiness.kt` (enum + loader), `core/nudge/
  NudgePolicy.kt` (exhaustive copy), `feature/setup/SetupViewModel.kt`
  (phoneOnly + steps + load), `MainActivity.kt` (routing, 2 sites). Tests:
  `ProfileCompletionViewModelTest` (+2 phone tests), stub helpers in
  `HomeViewModelTest` + `ProfileCompletionViewModelTest` gained a `phoneE164`
  param (default present).
- swift: mirror — `Core/Profile/ProfileReadiness.swift`, `Core/Nudge/
  NudgePolicy.swift`, `Feature/Setup/SetupViewModel.swift`,
  `Feature/Profile/ProfileCompletionScreen.swift`, `AttorneyShieldApp.swift`
  (routing, 2 sites). Same test additions + stub params.

## Test results

- **Android**: full `:app:testDebugUnitTest` — BUILD SUCCESSFUL. New: a phone-less
  member gets an outstanding "Add your phone number" row (9 rows, not complete);
  a member with a phone gets none (8 rows, complete).
- **iOS**: full `AttorneyShieldTests` target — TEST SUCCEEDED (mirrored tests).

## Gotcha worth recording

Mid-work I had **several `xcodebuild test` processes running concurrently**
against the same DerivedData/scheme. They stomped each other and produced
*spurious* failures — including pure tests that can't fail from this change
(`ProfileReadinessTests.markingTouchesNoOtherStep`) and "unable to create file
Tests/Samples/Issues/…json" build errors from the Lottie package. Killing the
stray processes and running **single-process** (`-parallel-testing-enabled NO`)
showed everything green. Lesson: one xcodebuild at a time per scheme; don't fire
a re-run before the previous one is dead.

## Decisions

- **Missing-only** (`phoneE164 == nil`), not "unverified": web stores but never
  verifies, so gating on `phoneVerifiedAt` would nag every web registrant. The
  stated risk was a *missing* number; this targets exactly that.
- Reused the existing 08/09 panes and the checklist-editor pattern rather than
  building a native Stage-4 wizard — the member registers/pays on web, so a full
  linear 08→12 flow would mostly re-collect what web already has.

## Open

- Live screenshot pending (emulator session expired).
- Disk on this machine is chronically near-full (~10 GiB); cleared DerivedData +
  sim caches twice this session.
