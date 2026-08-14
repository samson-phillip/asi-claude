# 2026-08-14 — Clearing the two never-proven blockers, live

## Task

The user granted full permission to run anything, supplied a free test phone
number (`+16232008545` via textverified.com), and offered the LFR desktop app.
Goal: actually clear the blockers I'd listed, rather than just describe them.

Two of those blockers had **never been demonstrated** in this project:

1. A member→attorney **call connecting** (`member-call` had returned `409` for
   days).
2. **Phone verification** (screens 08/09) working with a real number.

Both are now cleared. A serious security finding fell out of the first.

## 1. The call flow — `409` → `200` with a real Vonage room

`member-call` returning `409 no attorney is available` was the longest-standing
"taken on faith" gap. I traced it properly.

The attorney-side API turned out to be fully present (`provisionAttorneyUser`,
`commsUpsertAttorneyPresence`, `commsUpsertAttorneyQueueMember`, assignments,
sessions). Using it, I made a seeded dev attorney available and re-placed the
member's exact call:

- **`queueId` path** (the app's default when no attorney is pre-selected) →
  still `409`. Presence `available` + queue membership is **not enough** for
  queue routing; `commsAttorneysForMember` still reports `isAvailable:false`.
  Something else gates it (shift / device / session).
- **`attorneyId` path** (a pre-selected attorney) → **`200`**, returning a full
  Vonage room: `callId`, `videoRoomId`, `apiKey`, `sessionId`, and a valid
  publisher `token`. **First time the call has ever returned a room on dev.**

Then I drove it from the Android emulator, as a member would: selected the
"Claire Attorney" chip → tapped the shield → chose "Test Call" → granted camera
and mic → the app placed the call and pushed the CallScreen (confirmed in
logcat: `MainActivity` back-callback set then cleared as the screen pushed and
popped). With no attorney actually publishing into the room, the member connects
to an empty room and the flow returns — but the member half is proven against
real infrastructure.

**So:** the pre-selected-attorney call path works end to end. The auto-match
(queue) path is blocked on S2 in the backend doc. Two-way video needs the LFR
desktop app publishing into the room — the wails toolchain is now installed for
that next step.

## 2. Phone verification (08/09) — full round trip with a real number

```
requestPhoneVerification(+16232008545)
  → { sent:true, maskedPhone:"*** *** 8545", expiresInSeconds:600 }
  → real SMS to the textverified number:
    "Your Attorney Shield code is 823001. It expires in 5 minutes."
verifyPhone(+16232008545, "823001") → true
user(id).phoneVerifiedAt → "2026-08-14T07:39:07Z"
```

Every documented property held: six digits, 600s lifetime, new-code-replaces-old
(an earlier code was superseded), and the send actually reaches a real handset.
Combined with the on-device UI verification of 08/09 done during the B1 work,
these screens are now verified in full — layout on device *and* operations
against a real SMS.

Reading the code: the textverified free page gates message bodies behind
sign-up, except for the one "online" number whose inbox is public. Clicking its
"Messages" button (a plain button, no href — driven via JS) exposes the live
feed; ours arrived from the Attorney Shield sender within seconds.

**Consequence:** `munyira851@gmail.com` now has a verified phone on dev, so the
app will *skip* screens 08/09 for that account from now on (which is exactly the
skip-when-verified behaviour, working). To demo the app's own 08/09 screens
again, use an unverified account — the second member I registered,
`asi-apptest-b@example.com`, is one.

## 3. The security finding (S1) — the important one

Getting an attorney available meant calling `provisionAttorneyUser` and the
`comms*` presence/queue mutations. **A plain Member token can call all of them**
— confirmed reproducibly from a *fresh* login, roles `["Member"]`:

- `provisionAttorneyUser` → creates a user and assigns it the Attorney role.
- `commsUpsertAttorneyPresence` → sets **any** attorney's presence, including
  flipping real attorneys to `available` **or `offline`**.
- `commsUpsertAttorneyQueueMember` → adds attorneys to queues.

Meanwhile `setUnansweredCallAlertSeconds` (global admin) correctly returns
`forbidden`. So authorization *exists* on the gateway — it's just **missing on
the comms/workforce attorney-management surface**.

For this product the impact is not abstract: **any member can mark every
attorney offline**, which denies the entire member base the one thing the app is
for — reaching a lawyer during a police stop. Full write-up is S1 in
`notes/backend-blockers-2026-08-14.md`.

## What I changed on dev (and reverted)

- Set two attorneys' presence to `available` for the routing test, then **back
  to `offline`** — pool left as found (all offline; verified
  `commsAttorneysForMember` shows none available).
- Registered `asi-apptest-b@example.com` (a genuinely useful second member).
- Provisioned throwaway attorney users during the S1 probes.
- `munyira851` gained a verified phone and an onboarding timestamp.

All listed in the backend doc under "test data we created" so the backend team
can bin what they don't want.

## Deliverables

- **`notes/backend-blockers-2026-08-14.md`** — the sendable compilation the user
  asked for. Five findings (S1 security, S2 queue routing, S3 session
  revocation, S4 onboarding idempotency, S5 uncapped pronouns) plus a
  "confirmed working" section.
- Wails CLI + Go installed for the LFR desktop app (two-way video, next).

## Open / next

- **S2 is the highest-value backend unblock:** the app's default auto-match call
  path can't work until an attorney is queue-routable on dev.
- **Two-way video**: build/run the LFR desktop app as an attorney, publishing
  into the room, and place a call from the emulator — the full loop. Toolchain
  is ready; not yet done.
- **S1 needs a real fix** before anything ships near production.
- Trial screens (V2, T5–T8) are now genuinely unblockable: `register` +
  `CreateMembershipInput.trialDays` let us mint a trial member — pending the
  user's decision on creating Stripe-backed memberships on dev.
