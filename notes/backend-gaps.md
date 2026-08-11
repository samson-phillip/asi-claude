# Backend gaps and blockers

Running register of everything the mobile apps need from the backend that does
not exist, is undocumented, or is unreachable. Keep it updated as things are
answered — this is the list we take to the backend team.

**Status key:** 🔴 blocking now · 🟠 blocks a later phase · 🟡 question, not a blocker

Last updated: 2026-08-11 (deep links)

---

## 🔴 Blocking now

### 1. GraphQL gateway URL
`member-client` is served same-origin behind a proxy, so `GRAPHQL_URL` is just
`/query` and the real host appears nowhere in the repo. Native apps have no
origin to be relative to and need the absolute URL.

- **Need:** the gateway base URL per environment (dev, staging, prod).
- **Blocks:** any real login. Everything after it.
- **Interim:** `AsiConfig.Dev.graphqlUrl` points at the comms host as a
  placeholder that fails loudly rather than silently hitting the wrong service.

We know the comms REST service is `https://comms-dev.attorneyshield.io` (from
`serve-proxy.mjs`) and that it works — a `member-call` request returned a
well-formed `409`.

---

## 🟠 Blocks a later phase

### 2. Token refresh
`login` returns a `refreshToken`, but `api.ts` never sends it and no refresh
operation is documented.

- **Need:** is there a refresh mutation? If so, its shape and the access-token
  lifetime.
- **Why it matters more on mobile:** a web tab is usually short-lived; a native
  app sits backgrounded for days. Without refresh the only correct behaviour is
  to detect an auth failure and bounce the member back to login — which, for an
  app someone opens *during a police stop*, is the worst possible moment.
- **Blocks:** Phase 2 completion (the decision, not the code).

### 3. Sign-in by one-time code
The design reference (screen 13A) says: *"A password makes sign-in faster on
this device. You can always sign in with a one-time text code instead."* There
is no OTP endpoint in the documented API.

- **Need:** does a request-code / verify-code pair exist?
- **Blocks:** the reference's actual sign-in flow. We are building
  email + password only, which the API does support.

### 4. Native registration (screens 08–12)
Phone entry, SMS verification, personal details, address, and a 4-digit PIN.
**No endpoints exist for any of it.**

- **Need:** confirmation these are planned, plus shapes when they are.
- **Note:** payment itself is *not* a gap — checkout is web (Stripe on
  `attorney-shield.com`), and the app resumes at screen 08 after a deep link.

### 5. Post-registration feature set
None of these have endpoints:

| Feature | Screens |
|---|---|
| Document vault ("Digital Glovebox") | 14, 14A–14D, 31 |
| Situation preferences (pick 3) | 13B, 13C, 27B |
| Activity timeline | 32 |
| Plan / payment method / family sub-accounts | 33A, 33B, 33D |
| Notifications & nudge system | 15, 22–26 |
| Trial gate + in-app conversion | V2, T5–T8 |
| Guest sessions & gates | G1–G3 |

- **Blocks:** Phase 3 entirely. Cannot be scoped until answered.

### 6a. Domain association files for the deep link (web task)

The apps now handle the web→app handoff, but the links cannot open the app
*silently* without domain verification files served from both
`attorney-shield.com` and `www.attorney-shield.com`:

- **Android:** `/.well-known/assetlinks.json` carrying the app's signing
  certificate SHA-256 fingerprint for `com.app.attorney.shield`.
- **iOS:** `/.well-known/apple-app-site-association` for the app's Team ID +
  `com.app.attorney.shield`, plus an Associated Domains entitlement on our side.

Until both exist, Android shows a disambiguation dialog and iOS Universal Links
do not fire at all. Interim: a private scheme (`attorneyshield://return`) works
today and also backs the reference's "Open app manually" fallback.

### 6. Deep-link contract for the web→app handoff
Screens 07 and T4 hand back to the app with "email pre-filled". The reference
also plans to branch by origin (app-initiated vs website-mobile).

- **Need:** the exact URL scheme / universal-link path and its parameters, plus
  whether the link carries anything trust-bearing.
- **Security note:** we will treat the link as untrusted input and let the
  backend decide entitlement — a deep link must never itself grant access.
- **Blocks:** Phase 2's deep-link handler.

---

## 🟡 Questions, not blockers

### 7. `member-call` has no authentication
The comms endpoint accepts an unauthenticated POST today. We are not designing
around that — just flagging it, since it lets anyone place a call against any
`organizationId`/`memberUserId` they can guess.

### 8. Dev test credentials
We have `DEV_DEFAULTS` (org, jurisdiction, queue) but no dev member login.

- **Need:** a test email/password on `ias_dev` so we can exercise the real flow.

### 9. An attorney online on dev
`member-call` currently returns `409 no attorney is available to take this
call`, which is correct behaviour and confirms the contract — but it means we
cannot yet prove a video session goes **live** end to end.

- **Need:** a window with a dev attorney available, or a way to seed one.

### 10. Error/danger colour
Not a backend question — for Blue Sky Marketing. The palette forbids the red it
names and supplies no error colour, but the call flow needs an error state and a
hang-up control.

---

## Answered / closed

*(nothing yet)*
