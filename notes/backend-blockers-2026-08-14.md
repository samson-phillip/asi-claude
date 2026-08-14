# Backend blockers & findings — 2026-08-14

Compiled for the backend team. Everything here was verified live against
`gateway-dev.attorneyshield.io` / `comms-dev.attorneyshield.io` today, with a
plain **Member** account (`munyira851@gmail.com`, roles `["Member"]`) unless
noted. Ordered by severity.

---

## 🔴 S1 — A Member token can run attorney-workforce admin operations

**This is the most important item in this document.** It is a live
authorization hole on dev, reproducible from a fresh login.

A plain member token — no admin role — successfully calls:

| Mutation | What it did | Verified |
|---|---|---|
| `provisionAttorneyUser(organizationID, email, displayName)` | Created a user **and assigned it the "Attorney" role** for the org. Returned the new user id. | ✅ 200, twice, fresh tokens |
| `commsUpsertAttorneyPresence(input)` | Set **any** attorney's presence — including flipping a real seeded attorney to `available` **and to `offline`** | ✅ |
| `commsUpsertAttorneyQueueMember(input)` | Added an attorney to a call queue | ✅ |

The gateway **does** correctly gate other admin mutations from the same token —
`setUnansweredCallAlertSeconds` returns `forbidden`. So the check exists in
places; it is **missing on `provisionAttorneyUser` and the `comms*`
attorney-management surface** (presence, queue, devices, sessions, call
assignments all appear to be in the same ungated group).

**Why this is severe for this product specifically.** The app exists to reach a
lawyer during a police stop. With this hole, any signed-in member can:

- **Mark every attorney `offline`** → nobody in the pool is routable → every
  member's "connect to an attorney" fails. A denial-of-service on the core
  safety promise, from an ordinary member account.
- **Provision fake "attorneys"** and insert them into queues → route real
  members in a live encounter to an endpoint the attacker controls.
- Manipulate call assignments and presence for other attorneys.

**Ask:** role-gate `provisionAttorneyUser` and the entire `comms*`
attorney/agent/presence/queue/assignment mutation surface to admin/workforce
roles. Members should have **read**, at most, of `commsAttorneysForMember`.

*(Note: `register` is also open on dev — "Create a user with a password
credential. For production you will likely restrict this." Expected for a dev
convenience; flagging so it is on the list for the production lock-down.)*

---

## 🟠 S2 — Queue routing can't be satisfied on dev; only direct-attorney works

The member app's **default** path is queue-based (a member who doesn't
pre-select an attorney sends `queueId`, not `attorneyId`). That path has
returned `409 no attorney is available` for as long as we've been testing.

Today we isolated why. With a real attorney (`Dev Attorney`,
`de300000-…-000001`) in the dev queue `4b8e0610-…` **and** presence set to
`available`:

- **`member-call` with `queueId`** → still `409`.
- **`member-call` with `attorneyId`** (same attorney) → **`200`**, with a full,
  valid Vonage room (`callId`, `videoRoomId`, `apiKey`, `sessionId`, publisher
  `token`).

So `commsUpsertAttorneyPresence(state:"available")` + queue membership is **not
sufficient** to make an attorney routable through a queue —
`commsAttorneysForMember` still reports `isAvailable:false` for them. Something
else (an active shift? a registered device with a heartbeat? an active session?)
gates queue availability, and the presence mutation alone doesn't set it.

**This is the single thing keeping the member app's primary call path from
working end to end.**

**Ask:** either (a) tell us the full set of preconditions for an attorney to be
queue-routable on dev so we can seed a working attorney, or (b) seed one
permanently-available dev attorney in queue `4b8e0610-…` for org
`de200000-…-0001` / jurisdiction `de400000-…-0001`. Then the member app's
auto-match path is testable.

**Update — ran the real LFR desktop app as an attorney (2026-08-14 PM).** Built
and launched `lfr-desktop`, logged in, went online, and confirmed via its own
log that it polls `commsCallsAssignedToAttorney` for the seeded attorney
`de300000-…020001` (Claire). Findings:

- **Presence is not durable.** `commsUpsertAttorneyPresence(state:"available")`
  makes a member-call to that attorney return `200` for a short window, but the
  attorney reverts to unroutable quickly with no heartbeat to keep them up. Some
  calls to Claire held `ringing` ~25s; others timed out in seconds under
  identical setup. The routing/availability layer on dev is **non-deterministic**
  from the client's side.
- **A discrepancy worth a look:** with a live `ringing` assignment for Claire
  (confirmed by `commsCallsAssignedToAttorney` returning it for our token), the
  desktop app's *own* poll of the same query, same token, same attorneyId,
  returned **empty** — its "Incoming calls" stayed 0. We could not see the
  desktop's console (production build), and it is read-only for us, so we could
  not instrument it. Flagging in case the query behaves differently under the
  attorney client's exact call shape, or there is a scoping rule we are missing.

Net: the **member half** and the **plumbing** are proven (a real Vonage room,
both parties issued publisher tokens for the same session). A **live two-way
video call could not be completed on dev** because an attorney cannot be held
reliably routable long enough to accept — the same root cause as S2.

**Good news within this:** the **pre-selected-attorney** path is now proven end
to end. `member-call` returns a real room; the Android app drives the whole flow
(attorney chip → shield → situation → camera/mic permission → call screen →
`member-call` → room). This is the first time the call has ever returned a room
on dev. Two-way video (an attorney publishing into the room) still needs the
LFR desktop app running concurrently, which is the next thing we're setting up.

---

## 🟠 S3 — `otherSessionsRevoked: true` doesn't actually revoke

Signed in twice as the same member. The second login returned
`otherSessionsRevoked: true`. Then, using the **first** session's tokens:

- its **access token** still returned `200` on authenticated queries;
- its **refresh token** still refreshed successfully (minted a new valid pair).

So the older device is **not** signed out, and because its refresh token keeps
working it can renew indefinitely. One-device-at-a-time is **reported but never
enforced** — presumably stateless JWTs plus a `sessions` row that nothing checks
against.

**Why it matters beyond tidiness:** we surface this to members — the app shows
"Your account was opened on another device" on the strength of that flag. Right
now the product is telling members a security property holds when it does not.

**Ask:** confirm whether single-device is intended. If yes, the tokens need to
be checked against session state (or short-lived + a revocation list). If no,
stop returning `otherSessionsRevoked: true`, and we'll drop the messaging.

---

## 🟡 S4 — `completeMyOnboarding` is not idempotent (contradicts its own docs)

Its schema description says *"Idempotent — calling it again keeps the original
timestamp."* It does not. Two calls a second apart:

```
call 1 → onboardingCompletedAt: 2026-08-14T05:27:56Z
call 2 → onboardingCompletedAt: 2026-08-14T05:27:57Z
```

Each call overwrites the timestamp. We guard against re-calling it, so **our**
clients won't cause drift — but any client that trusts the "idempotent" contract
and calls it more than once turns "when this member finished setup" into "when a
client last called this."

**Ask:** make it match its description (first write wins), or correct the
description.

---

## 🟡 S5 — `notificationFrequency` / `pronouns` have no length or value guard we can see

Minor, and we've worked around both:

- **`notificationFrequency`** *is* validated (rejects anything but
  `occasionally|rarely|off`, case-insensitive) — thank you, that's correct.
- **`pronouns`** has **no length cap** — a 300-character value was accepted in
  full. We cap at 40 client-side, so our writes are safe, but anything else
  writing to this field could store a paragraph.

**Ask (low):** a server-side length bound on `pronouns`.

---

## ✅ Confirmed working today (no action needed — recording for confidence)

- **Phone verification round trip (screens 08/09), end to end with a real
  number.** `requestPhoneVerification(+1…8545)` → real SMS delivered ("Your
  Attorney Shield code is 823001. It expires in 5 minutes.") → `verifyPhone` →
  `phoneVerifiedAt` stamped. The six-digit code, the 600s lifetime, the
  new-code-replaces-old rule, and the five-sends-an-hour limit all behave as
  documented.
- **`member-call` returns a real Vonage room** when an attorney is reachable by
  `attorneyId` (see S2).
- **`refreshToken`** rotates and is single-use (a re-used token returns
  `session expired`) — C2 is wired against this.
- **`convertMyTrial`** exists and is self-scoped; fails cleanly with no default
  payment method (the error the trial gate must handle).

---

## Test data we created on dev today (for your cleanup, if you want it)

- Registered member `asi-apptest-b@example.com` / `Test@123` (we needed a second
  member; happy to keep or bin it).
- Provisioned attorney users `asi-attorney-test@example.com`,
  `sec-probe@example.com` (from the S1 probes).
- `munyira851@gmail.com` now has a **verified phone** (`+16232008545`, a shared
  public test number) and `onboardingCompletedAt` set.
- Set `Dev Attorney` / `Claire Attorney` presence to `available` during testing,
  then **back to `offline`** — the pool is as we found it (all offline).
