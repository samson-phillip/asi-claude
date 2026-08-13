# Backend gaps and blockers

Running register of what the mobile apps need from the backend.

**Status key:** BLOCKING = stopped now · HIGH = blocks a phase · LATER = needed,
not urgent.

Last updated: 2026-08-12, after introspecting the live gateway.

---

## Correction: most of this list was wrong

Earlier versions claimed registration, the document vault, family sub-accounts,
notifications, OTP sign-in and token refresh had no endpoints. **They all exist.**

The error was ours: we inferred the API surface from the operations
`member-client` happens to use, rather than asking the gateway. It has **238
queries and 297 mutations** and introspection is enabled at
`https://gateway-dev.attorneyshield.io/query`.

Lesson worth keeping: introspect the schema before concluding anything is
missing.

---

## Resolved

| Item | Resolution |
|---|---|
| GraphQL gateway URL | `https://gateway-dev.attorneyshield.io/query` — was in `lfr-desktop/.env.example` all along |
| Dev member account | Supplied; sign-in verified end to end on Android |
| Token refresh | `refreshToken(input: RefreshTokenInput)` |
| OTP sign-in | `requestLoginOtp(email, channel)` / `verifyLoginOtp(email, code, countryISO2)` |
| Registration 08–12 | `register`, `createUserProfile`, `createUserAddress`, `setMemberPin`, `verifyMemberPin`, `memberPinStatus` |
| Document vault | `createUserDocument`, `deleteUserDocument`, `adminDocumentTypeList`, request/finalize upload pattern |
| Family / plan / payment | `addSubaccount`, `changeMembershipSeats`, `changeMembershipPlan`, `attachPaymentMethod`, `createSetupIntent` |
| Notifications | `notificationList`, `markNotificationRead`, `markAllNotificationsRead`, `clearNotifications`, `registerWebPush` |
| Emergency contacts | Full CRUD |
| Activity | `biMemberActivity` |

---

## Still open

### 1. Dev data is empty — BLOCKING

`adminIncidentTypeList(activeOnly: false)` returns `[]` and the test member has
no cases. No errors — there is simply nothing seeded. Home correctly shows its
empty state, which means the tile grid, attorney chips and a real incident-typed
call cannot be exercised.

**Need:** incident types (with translations) and a case for the test member.

### 2. No attorney has ever been online — HIGH

`member-call` returns `409`. Going online is
`commsUpsertAttorneyQueueMember(queueId, attorneyId, role, weight)` with a wider
presence model behind it (`attorneyPresence`, `attorneyActiveSession`,
`attorneyDevice`).

**Need:** an attorney account, or someone to run `lfr-desktop` for a window. We
have not done this ourselves — shared environment, and it would make someone
appear available for real calls.

### 3. Shape confirmations — HIGH

`OtpChannel` enum values; whether `countryISO2` is required and what it should
be; whether `verifyLoginOtp` returns the same shape as `login`; access-token
lifetime and whether refresh rotates; whether `verifyMemberPin` is the intended
server-side gate for ending a call.

### 4. Genuinely absent from the schema — HIGH

- **Situation preferences** (13B, 13C, 27B). No `situation` / `preference` /
  `favourite` operations. Home shows the full list because there is nowhere to
  store a choice.
- **Trial and guest** (V1–V2, T1–T8, G1–G3). No `trial` / `guest` operations. Is
  a guest a real account with a role, or local-only state?

### 5. Deep-link contract — HIGH

Real path and parameter names. We accept `/app/return`, `/return-to-app`, `/app`
with an `email` parameter, confined to one file. The link must not carry a
credential — we treat it as untrusted input.

### 6. Domain verification files — HIGH (web task)

`assetlinks.json` and `apple-app-site-association` on both hosts, for
`com.app.attorney.shield`. Blocked on us producing a release keystore first.

### 7. `member-call` has no authentication — LATER

Anyone can place a call against any org/member ID they can guess, and it routes
to a real attorney. Flagged, not designed around.

### 8. Error/danger colour — LATER (Blue Sky, not backend)

The palette forbids the red it names and supplies no error colour, but the call
flow needs an error state and a hang-up control.
