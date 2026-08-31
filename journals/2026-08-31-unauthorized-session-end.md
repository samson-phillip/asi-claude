# 2026-08-31 — Handle a dead token instead of leaking "unauthorized"

## The bug (from the member's logs + screenshot)

A relaunch with a stale/expired token left the app on a **half-loaded Home**: the
greeting and readiness card rendered, but every query 401'd, "No incident types
are configured yet", and a raw **"unauthorized" error banner** was shown to the
member. The console flooded with:

```
[AsiApi] GraphQL error · query IncidentTypes { · unauthorized
[AsiApi] GraphQL error · query User($id: ID!) { · unauthorized
… (one per query)
```

(The `Failed to send CA Event … app_launch_measurement` lines are Apple's launch
metrics, not ours — left alone.)

## Root cause

The gateway returns a dead token as **HTTP 200 with a GraphQL error
`unauthorized`**, not a 401. Both apps only recognised auth failure on a 401
status — so:
- The token-refresh / session-end machinery (which *is* wired and correct) never
  fired.
- Every query instead threw a generic error, logged line-per-query, and each
  screen surfaced the raw `"unauthorized"` string.
- The member was stranded, because the app only navigates to Login when a
  **session-ended reason** is set, and nothing set it.

## Fix (both platforms)

1. **Recognise the 200-unauthorized.** In the transport, a 200 body whose
   top-level GraphQL errors say `unauthorized`/`unauthenticated` now throws the
   same `UnauthorizedError`/`UnauthorizedException` a 401 does — so it takes the
   existing refresh→retry→end path, and is no longer logged per-query.
   - swift: `AsiApi.gqlOnce` + `isUnauthorized(_:)`.
   - kotlin: `AsiApi.postOnce` + `isUnauthorizedGraphql(_)` (with a cheap
     `contains("\"errors\"")` gate so normal data responses aren't re-parsed);
     new `GqlErrorsOnly` model. Placed in `postOnce` because that's where the
     retry wraps, keeping 401 and 200-unauthorized on one path.
2. **End the session with a reason.** When the refresh can't renew the token, the
   session now ends with *"Your session has expired. Please sign in again."*
   instead of a silent clear — which is what carries the member to Login (the app
   watches the ended-reason) and greets them with an explanation.
   - swift: new `SessionManager.endExpiredSession()`; called from
     `refreshExpiredToken`'s two failure paths.
   - kotlin: `refreshExpiredToken` now calls the existing `endSession(reason)`
     (this closes the open concern noted in the code: "returned to sign-in with
     no explanation … Noted in notes/open-concerns.md").

Net effect: an expired session → one quiet refresh attempt → Login with a clear
notice. No banner leak, no log flood, no stranded Home.

## Not done (deliberately)

- Didn't touch the per-VM error handling to swallow `UnauthorizedError` — the
  session-end redirect fires first, so the transient banner isn't seen. Kept the
  change to the transport + session layer.
- The refresh path is safe from recursion: `refreshTokens` is `authed: false`, so
  its own unauthorized can't re-trigger the refresh; the refresher is also
  single-flight (actor / one-at-a-time), so a barrage of concurrent unauthorized
  queries triggers exactly one refresh and one session-end.

## Test results

- **Android**: full `:app:testDebugUnitTest` — BUILD SUCCESSFUL. New: a 200
  unauthorized GraphQL error throws `UnauthorizedException`; a token that can't
  refresh ends the session with an "expired" reason + clears storage.
- **iOS**: full `AttorneyShieldTests` — TEST SUCCEEDED (mirrored tests).

## Process note

Wasted time earlier chasing *spurious* Swift test failures that turned out to be
**several concurrent `xcodebuild` runs** stomping the shared build. Running
single-process (`-parallel-testing-enabled NO`) after killing strays was clean.
One xcodebuild per scheme at a time.
