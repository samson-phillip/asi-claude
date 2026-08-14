# 2026-08-14 — C2 (token refresh) and C8 (the onboarding flag)

## Task

Two pieces of plumbing rather than screens.

**C2** — wire token refresh. We had never done it, because the behaviour we
needed to know was unanswered: how long does an access token last, and does
refreshing rotate the refresh token? Until that was answered, a 401 ended the
session.

**C8** — stop inferring "this member finished setup" from five other fields and
read the backend's own flag.

## Repos and files touched

### `kotlin`
| File | What |
|---|---|
| `core/session/TokenRefresher.kt` | **New.** One in-flight refresh, shared. |
| `core/session/MemberContext.kt` | Persist the refresh token. |
| `core/session/SessionManager.kt` | The refresh-and-retry hook; rotate in place. |
| `core/network/AsiApi.kt` | `refreshTokens`, `completeMyOnboarding`, one retry per 401. |
| `core/network/Models.kt` | Wire types; `onboardingCompletedAt`. |
| `core/profile/ProfileReadiness.kt` | `isOnboarded`. |
| `feature/profile/ProfileCompletionViewModel.kt` | Stamp when the last row ticks. |
| `MainActivity.kt` | Route on the flag. |
| `core/session/TokenRefresherTest.kt` (new), `SessionManagerTest.kt` | Tests. |

### `swift`
Same shape, with `Core/Session/TokenRefresher.swift` as an **actor** — the actor
gives mutual exclusion for free, so the check-and-set that decides whether to
start an exchange cannot interleave, which is the entire correctness
requirement. Plus `AttorneyShieldTests/TokenRefresherTests.swift`.

## C2 — what the backend told us, and what we verified

Their answer:

- Access token: **6 hours**. Refresh token: **30 days**.
- **Refresh rotates.** Each refresh token is single-use.

And the warning that came with it, which is the actual design:

> Never fire two refreshes with the same token. Opening the app after the access
> token expires fires a burst of parallel queries that all 401 at once. If each
> launches its own refresh, the first rotates the token, every other presents a
> spent one, gets told the session is gone, and signs the member out — even
> though the refresh token was good for another 30 days.

**Verified rather than trusted.** Against dev: refreshing returns a new pair,
and presenting the same refresh token a second time returns `session expired`.
So the trap is real.

### The implementation

`TokenRefresher` holds one in-flight attempt. Everyone who arrives while it is
running joins it and receives its result; nobody spends a second token. Once it
finishes, the slot clears — a token minted now can expire later, and a future
401 deserves a real second attempt rather than a cached answer.

A 401 buys **one** refresh and **one** retry. A second 401 on the retry means
the new token was rejected too, which is a dead session rather than an expired
one; retrying again would loop.

The rotated refresh token replaces the spent one **everywhere**, storage
included. Persisting the old one would mean the next wake-up presents something
already burned — the same bug by a slower route.

The refresh call is unauthenticated, and there is a test for it. Attaching the
access token this is meant to replace would fail the request for exactly the
reason we are there.

## C8 — the flag, or the rows

`isOnboarded` is **`onboardingCompletedAt` set, or every row ticked** — not the
flag alone.

The flag alone would send every existing member back through a checklist they
had already finished, because nobody has the stamp yet. The rows alone were the
old inference, which silently changed meaning every time a row was added:
introducing "your common situations" quietly made previously-complete members
incomplete again.

Taking either means the flag can only ever *settle* the question, never reopen
it.

**Scope, deliberately narrow:** `isOnboarded` governs **routing** — do we push
this member into setup. The checklist rows, the readiness card and the nudges
still run off the per-row inference, because those are about individual gaps
("add an emergency contact"), not about whether onboarding is over. A stamped
member with no PIN should still be told about the PIN.

## Two things the probes turned up

Both raised with the backend; neither blocks us.

### 1. `completeMyOnboarding` is not idempotent

Its own description says *"Idempotent — calling it again keeps the original
timestamp."* Two calls a second apart:

```
05:27:56Z
05:27:57Z
```

It overwrites. Left unguarded, the field would drift into meaning "when the app
last noticed" rather than "when this member finished setup". Our
`onboardingCompletedAt.isNullOrBlank()` guard prevents that — it was written as
an optimisation and is now load-bearing, with a comment saying so on both
platforms.

### 2. `otherSessionsRevoked: true` does not revoke anything

Signed in as session A, then again as session B. B reported
`otherSessionsRevoked: true`. Then, with A's tokens:

- A's **access token** still returned `200`.
- A's **refresh token** still refreshed successfully.

So the old device is not locked out at all — and since its refresh token keeps
working, it can renew indefinitely. The tokens are stateless JWTs, so this is
presumably "the session row is marked, the tokens are not checked against it".

That matters twice over. It is a **security expectation the product states and
does not meet** — and we surface it to members ("Your account was opened on
another device"), which makes the app the thing telling them something untrue.

## Test results

**Android — 405 tests, 0 failures.** **iOS — 382 tests, 0 failures.**

New: `TokenRefresherTest` / `TokenRefresherTests` (5 and 4) covering the burst,
the rotation, the no-replay rule and a shared failure; plus 4 `SessionManager`
tests for refresh-and-retry, the unauthenticated refresh, sign-out on a refused
refresh, and retry-exactly-once.

## What is and is not verified live

Being precise, because the distinction matters:

- **Verified against dev by hand:** `refreshToken` works, rotates, and is
  single-use; `completeMyOnboarding` works and overwrites; session revocation
  does not revoke.
- **Verified in tests against a real 401:** the full 401 → refresh → retry path,
  through MockWebServer / `StubURLProtocol`.
- **Not verified on a device end to end:** an actual expired-token refresh. It
  needs a 6-hour-old access token, and the one lever that would have forced a
  401 early — signing in elsewhere — turns out not to invalidate anything (see
  above). Worth revisiting once revocation works, or with a short-lived token on
  a test account.

## Open issues / next steps

- **Ask for a short-lived-token switch on dev**, or a way to invalidate an
  access token, so refresh can be exercised on a device without waiting 6 hours.
- Still queued: **B8b** (what `kind` means; somewhere for per-member app state).
- Screens **08/09** still need a real phone number for live verification.
- Trial screens **V2, T5–T8** still blocked on a password for
  `tester6@ainnop.com`.
- With David: emergency-contact alert, guest model, specialty ordering.
