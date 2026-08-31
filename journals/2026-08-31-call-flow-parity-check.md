# 2026-08-31 — Call-flow parity check against member-client

## Task

Innocent has been changing `member-client` day to day and asked for parity checks
so the mobile apps stay corrected. Pulled member-client (`ab9f8ed` → `127ea35`,
20 commits / 64 files / +4,402−305) and audited the **call-flow** theme against
the kotlin + swift apps.

## What changed in member-client (call-flow-relevant)

| Commit | Change | Mobile status |
|---|---|---|
| `fcfb549` | "Stop guessing how the wait ended, and ask comms" — the connecting screen now follows comms' `isFinal` (`commsMemberCallState` query + a `call-state` Vonage signal), with an absolute local safety-net deadline, instead of a blind 45s `setTimeout`. | **Already at parity.** Mirrored the same day into `Core/Video/CallWatch.{swift,kt}` + `CallViewModel` (poll loop, `onSessionSignal`, absolute `safetyDeadline`). Behaviour compared line-by-line; the only deltas are deliberate mobile adaptations (a final `CONNECTED` keeps the "joining…" notice because the live screen is driven by the video stream arriving; an unrecognised final state stays on the safety net rather than inventing an outcome). |
| `0fc2343` | "The call sheet was invisible on any phone set to Light" — `.pin-sheet` drew its background from `--surface-2` (white in the light CSS palette) under white content, so the End-call PIN sheet vanished in Light mode; also a web button-wrap fix. | **N/A (web-only).** Mobile paints the call sheet in fixed Attorney-Shield navy, not CSS light/dark tokens, so the disappearing-sheet failure cannot occur; the button layout is native. |
| `1962ba4` | "Nudge the PIN at a calm moment" — `security-pin` joins member-client's readiness model + nudge catalogue; offered only at a calm app open, never from the call; ordered **second, behind the emergency contact and ahead of documents**. | **Mostly already present; one ordering fix applied** (below). |

## The one fix — nudge priority

The mobile apps already nudge the PIN at a calm moment (`NudgePolicy` has `.pin`
with benefit-first copy, gated by `isCalm`, never mid-call), and mobile's readiness
model already carries a `Pin` step (mobile's checklist is more granular than
member-client's five-item readiness). So 1962ba4's intent was already met — except
for **ordering**.

member-client's considered decision: the security PIN is first-tier — *"without one,
anybody holding the phone can end a live recorded consultation"*, a cost paid
**during** an encounter — so it sits second, ahead of documents (*"documents help
the attorney; they do not protect the member from the person standing over them"*).

Mobile's `NudgePolicy` priority had documents (and situations) **ahead** of pin:

```
before:  [contacts, documents, situations, pin, password, details, address]
after:   [contacts, pin, documents, situations, password, details, address]
```

Moved `.pin` to second on both platforms and rewrote the doc comment to carry the
safety rationale. So a member with no PIN and no documents is now nudged toward the
PIN first — the thing that protects *them* — matching member-client.

## Files

- `swift/AttorneyShield/Core/Nudge/NudgePolicy.swift`
- `kotlin/app/.../core/nudge/NudgePolicy.kt`
- Tests: `NudgePolicyTests.swift`, `NudgePolicyTest.kt` — ordering assertions
  updated (next-after-contacts is now `pin`; documents follows once the PIN is set).

## Tests

- Swift: `-only-testing:NudgePolicyTests` (single-process, iPhone 16 Pro) →
  **14 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `./gradlew testDebugUnitTest --tests …NudgePolicyTest` → **BUILD
  SUCCESSFUL**.

## Outcome / next

Call-flow parity: **the substantive work (the call-state watch) was already
mirrored**; this pass corrected the one real divergence (PIN nudge ordering) and
confirmed the Light-mode sheet fix is web-only. Remaining member-client drift lives
in other themes not touched here — money/currency, David's profile/account
feedback, country flags, and Google Places address autocomplete (the last needs a
native Places implementation, not a port). Those are queued for follow-up passes.
