# 2026-09-01 — Home/Profile empty after login: two `AsiApi` clients

## Symptom

After signing in, iOS Home showed the "there" greeting with empty tiles, **and**
the Edit-profile screen showed blank First/Last/Phone/**Email**. A blank email is
impossible for a populated `session.member` (the field is seeded directly from
it), so the member was genuinely **nil** across the whole view tree — even though
login had clearly succeeded.

## Diagnosis (via `[ASI]` console logs)

Added request/session logging. The tell was in the per-request line
`gql <op> → HTTP <status> · tokenSent=<bool>`:

- Every call made **by `SessionManager`** (`User`, `CasesByUser`,
  `MyAccountStatus`, `MySessionStatus`) → `tokenSent=true`.
- Every call made **by a view model** (`MyProfile`, `MemberPinStatus`,
  `EmergencyContacts`, `UserDocuments`, `CommonSituations`, `AttorneysForMember`,
  `IncidentTypes`) → `tokenSent=false` → gateway returns `200 + "unauthorized"` →
  `UnauthorizedError`.

The split is **by caller, not by timing** — impossible if both read the same
`authToken`. There were **two `AsiApi` instances**: `session` held the one whose
bearer token was set at login; the view models were built against a **different,
token-less** one.

`HomeViewModel.loadTypes()` catches the resulting `UnauthorizedError` and calls
`session.onUnauthorized()` → **sign-out** (member = nil). But `home`'s
`onSessionExpired` was the default no-op, so the app **stayed on Home** with a nil
member — greeting "there", empty tiles, blank profile. One nil member, all three
symptoms.

### Why two clients

Classic SwiftUI footgun. `RootView.init` creates `let client = AsiApi(config:)`
and wires it into the view models and the session. SwiftUI **re-runs a View's
`init`** on re-creation; `@State` keeps the values from the *first* init, but a
plain stored `let api` captured the *latest* client. So `session` (@State) held
client #1 while `self.api` held client #2. The account-switch `.onChange` I added
earlier rebuilt every view model with `self.api` (client #2, token-less) — which
is exactly why it worked before that change and broke after.

## Fix (`swift`)

- **`AttorneyShieldApp.swift`**
  - `api` is now **`@State`**, seeded once — it can no longer diverge from the
    `@State` `session`. This is the root fix (also covers `CallViewModel`, built
    from `self.api`).
  - **Removed** the `.onChange(of: session.member?.userId)` view-model rebuild.
    Its job (refresh each screen for the new account) is already done by the keyed
    `.task(id: session.member?.userId)` loads and the live-computed greeting, so
    switching accounts refreshes every screen **without** swapping instances — and
    without ever rebuilding against a stray client. Dropped the now-unused
    `sharedStore` property.
- **`SessionManager.swift`** — `onUnauthorized()` now sets `sessionEndedReason`
  (and is `@MainActor`) before signing out, so a genuinely rejected token routes
  to sign-in through the existing `sessionEndedReason` handler instead of
  stranding the member on a signed-out screen. Both callers (`HomeViewModel`,
  `TrialViewModel`) are already `@MainActor`.

## Diagnostics

Temporary `[ASI]` logs (request line with `tokenSent`, session lifecycle,
`home.load`/`loadTypes`) were added to find this and have been **removed** now
that it is fixed. They are what made the two-client split visible — the
`tokenSent=<bool>` field on every request was the whole diagnosis.

## Verified on device

Confirmed by the user: **both accounts now show correctly** (greeting by name,
populated tiles, filled profile) — on fresh sign-in and on account switch.

## A pre-existing test fixed along the way

The unit suite surfaced a stale test unrelated to this fix:
`AsiApiTests/aRejectedTokenOnTheMemberCallIsAnAuthFailure` enqueued a **403** and
expected `UnauthorizedError`. The sanctions commit (`4ad6fd3`) had reassigned a
member-call 403 to `SanctionedError` (an account block, not a logout) but never
updated this test, so it had been failing since then. A *rejected token* is a
**401**, so the test now enqueues 401; added
`aSanctionsBlockOnTheMemberCallIsNotALogout` to cover the 403 → `SanctionedError`
path (which had **zero** test coverage before).

## Tests / build

- iOS build **SUCCEEDED**.
- `AttorneyShieldTests` unit suite **545 pass, TEST SUCCEEDED**.
- The one remaining full-suite failure is
  `DynamicTypeUITests.testLoginStaysUsableAtTheLargestAccessibilitySize()` — a
  flaky accessibility UI test in the separate UI target, unrelated to this change
  (its sibling Dynamic Type tests pass).

## Files

- `swift/AttorneyShield/AttorneyShieldApp.swift`
- `swift/AttorneyShield/Core/Session/SessionManager.swift`
- (diagnostics) `swift/AttorneyShield/Core/Network/AsiApi.swift`,
  `swift/AttorneyShield/Feature/Home/HomeViewModel.swift`
