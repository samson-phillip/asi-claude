# 2026-09-08 — member-client parity: David V2 call fixes + Account→Documents sub-nav

## Context

Daily member-client parity pull. Since our last-seen `#147`, seven commits landed
on `member-client` dev; the mobile-relevant one is **`#155` — "Guest access at the
login door, and six fixes from David's V2 testing"** (plus `#157` web-funnel and a
documents fix `#151→#153` that is already backend-gated). Two parallel read-only
audits (kotlin + swift) graded both apps against the David-V2 checklist; I then read
member-client's actual `CallScreen.tsx` to pin the exact target before changing code.

Two audit findings were **corrected on inspection**:
- `"A valid PIN is required to end call."` is a **permanent hint** at the bottom of
  the PIN sheet (member-client `CallScreen.tsx:1372` `pin-sheet-hint`), **not** the
  wrong-PIN error. So mobile's `"That PIN didn't match. Try again."` error is fine;
  mobile was just **missing the standing hint line**.
- member-client's connecting-screen "cancel" is the **round red hangup control
  itself** (no PIN needed pre-live), not a separate labelled button.

## What already matched (no change)

- **Camera = flip, front default** — both apps cycle front/rear via a counter; not a mute.
- **Deactivated document type stays hidden** — both request `activeOnly:true` AND
  keep a client-side `isActive` filter. `#153` moved the gate into admin, so the
  phones obey it via the backend now regardless.
- **iOS §2.4 session reset** — audit said MISSING, but iOS already routes sign-out →
  `.welcome` and a fresh sign-in → `.completion` → `.home` (flat `destination`, no
  persistent `NavigationStack`), so a new session never lands on the old tab. No change.
- **Web-funnel items** (`#157` country-hidden, trial tile, guest login door) — N/A;
  mobile delegates registration/checkout to web and has no guest login door.

## What changed (both platforms, mirrored)

The PIN sheet + connecting screen (David V2 §2.7 / §2.9):

1. **Permanent hint** `"A valid PIN is required to end call."` on the PIN sheet (§2.7b).
2. **Help text reworked** to the exit that actually exists — *"Stay in the call and
   ask your attorney to end it for you. You can set a new PIN in Account afterwards."*
   — and revealed after **two failed attempts on any call**, not just via the Test-Call
   "Forgot PIN?" link (§2.7a). "Forgot PIN?" is now a tappable link (Test Call only)
   that reveals the same help; it no longer points at a Settings reset. Once the help
   shows, we stop repeating the wrong-PIN error (don't nag someone under pressure).
3. **Connecting subtitle dropped** (§2.9a): the standing "reaching the next available
   counsel / stay on this screen" line is gone; the slot now shows *only* the live
   comms narration (`connectingNotice`) when there is one.
4. **Cancel → round red control** (§2.9b): the connecting screen's text "Cancel" is now
   a 58×58 Live-Red circle with a white ✕ (mirrors the End control), no label.

Navigation (David V2 §2.6):

5. **Account → Documents (Glovebox) is a pushed route with a back arrow to Account.**
   Both shells use a flat `destination` (no back stack); opening the Glovebox from the
   Account menu now sets a `gloveboxFromAccount` flag, which (a) shows a back chevron on
   the Glovebox sections list and (b) makes its close return to Account. A tab tap
   clears the flag, so the Glovebox tab still opens as a root with no back arrow.
   (Only Documents is linked from Account on mobile — neither app links History from
   Account, so §2.6's "History" half is N/A here.)

State plumbing: `CallViewModel` gained `pinHelp` + `pinAttempts` (reset on
requestEnd/cancelPin, `pinAttempts++` on a wrong PIN, `showPinHelp()` for the link).

## Files

- **Kotlin:** `feature/call/CallViewModel.kt`, `feature/call/CallScreen.kt`,
  `MainActivity.kt`, `feature/glovebox/GloveboxScreen.kt`; test
  `feature/call/CallViewModelTest.kt` (+5 PIN/connecting cases).
- **Swift:** `Feature/Call/CallViewModel.swift`, `Feature/Call/CallScreen.swift`,
  `AttorneyShieldApp.swift`, `Feature/Glovebox/GloveboxScreen.swift`; test
  `AttorneyShieldTests/CallViewModelTests.swift` (+5 cases, `waitUntil` helper for the
  unstructured PIN Tasks).

## Status

- **Android: `:app:testDebugUnitTest` green** (full suite), including the 5 new cases.
- **iOS: `AttorneyShieldTests` green — `** TEST SUCCEEDED **`, 551 tests**, including
  the 5 new cases (a `waitUntil` helper polls the unstructured PIN Tasks).

## Not done / deferred

- **Guest login door** (`#155`/`#157`): a genuinely new *feature* on web (email → OTP,
  first/last name captured before the code). Mobile has no guest sign-in; this is a
  product decision, not a parity fix — flagged for Samson, not implemented.
- `#157` trial-as-tile and country-hidden: web purchase funnel only.
