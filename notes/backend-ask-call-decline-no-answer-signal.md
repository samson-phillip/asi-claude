# Backend ask — a real-time "declined / no-pickup" signal for the member

> **RESOLVED 2026-08-27 — C1 shipped (comms#81, member-client#128), adopted in
> both apps.** Backend delivered a `commsMemberCallState(callId)` query *and* a
> `call-state` Vonage session signal (dev + uat). Reply:
> `Downloads/2026-08-27-member-call-state-signal.md`. The apps now watch both
> through one `applyCallState`, act only on `isFinal` (a decline re-rings, it is
> not an ending), and replaced the 45s relative timer — which the backend flagged
> as a live defect — with an absolute safety net `max(waitStart+45s,
> ringExpiresAt+8s)`. See `journals/2026-08-27-c1-member-call-state-watch.md`.

**From:** Mobile (Android + iOS)
**Date:** 2026-08-27
**Context:** When the LFR **declines** a call — or simply doesn't pick up — the member
app has no real-time way to learn it. It waits out a **client-side 45s ring timeout**
and only then leaves the connecting screen. `member-client` behaves the same way, so
this is not a mobile-only gap; it's a missing capability on the shared API that would
improve **both** clients.

Checked against `member-client/src` and `lfr-desktop/app` directly. Kept to what needs
**your** input.

---

## What happens today

1. Member taps an incident → `POST /api/vonage/video/member-call` returns room
   credentials → the app shows **"Connecting you to an attorney."**
2. The backend rings an attorney (an attorney-call **assignment**).
3. **If the LFR declines**, the LFR desktop sends, in real time:
   `commsUpdateAttorneyCallAssignmentStatus(input: { id, status: "REJECTED", releasedAt })`
   (`lfr-desktop/app/app.go:2058` — *"REJECTED is what the decline button actually
   sends"*). So the **backend knows the instant of the decline.**
4. **If nobody picks up**, comms already detects it server-side — the
   `CANCEL_RING_TIMEOUT_SECONDS` sweeper (~30s) marks the call. So the **backend knows
   the no-answer too.**
5. **The member, however, is told nothing.** There is no member-facing call/assignment
   state to observe. The app just keeps showing "Connecting" until its own **45s ring
   timeout** fires, then it self-reports the outcome via
   `commsUpdateCallState(status: "no_answer")` and shows "No attorney picked up."

**Net effect:** a member can sit on the connecting screen for up to ~45s *after* the
LFR has already declined — the decision was made, but we can't act on it.

## What `member-client` has (so we can't just wire it)

- **Write only:** `endMemberCall` → `commsUpdateCallState(CommsUpdateCallStateInput)` —
  the member *reporting* the end (`no_answer`, `member_cancelled`, …) after its own
  timeout. There is **no read/subscribe** of live call or assignment state.
- No `commsCall(id)` / `callState` query, no subscription, no poll. `member-client`'s
  connecting screen is driven purely by `RING_TIMEOUT_SECONDS = 45` +
  `getCallNotAcceptedMessage()` copy. The decline never reaches it either.

So the operation genuinely isn't in the shared repo — this needs backend input, not
wiring on our side.

## The ask

Expose the **member-scoped, real-time state of the call the member just placed**, so
the client can leave the connecting screen the moment a decline / no-pickup is known
instead of waiting out the ring window. Any one of these works for us:

1. **Preferred — a subscription:** `commsCallState(callId: ID!)` pushing state
   transitions `ringing → assigned → (declined | no_answer | connected | cancelled)`,
   member-scoped by token.
2. **Acceptable — a lightweight poll:** the same as a query the app calls every ~2–3s
   while connecting: `commsCallState(callId: ID!) → { status, endReason }`. (The app
   already polls `mySessionStatus` on a timer, so this pattern is in place.)
3. **Also fine — a Vonage session signal** on the member's session when the assignment
   goes `REJECTED` / released. We already handle Vonage signals on this session
   (`signal:asr` for captions), so a `signal:call-state` would slot in.

Whichever is easiest on your side. The **status values we need to distinguish** are
already the ones you compute: **declined/rejected**, **no-answer/timed-out**, and
**connected** (so we can also drop the client timeout once the real signal exists).

## Priority / not a blocker

This is an **enhancement, not a blocker.** The ~45s client ring timeout is a working
fallback and both clients ship with it today — a member is never *stuck*, just made to
wait. The win is UX: reacting to a decline in ~1s instead of ~45s. It benefits the web
client identically.

## Summary

| # | Ask | Type | Benefit |
|---|---|---|---|
| C1 | A real-time member-facing **call-state** signal (subscription, poll, or Vonage signal) exposing **declined / no-answer / connected** | API gap | App + web leave "Connecting" the moment the LFR declines or times out, instead of after the 45s client ring timeout |

Backend already has both facts — the LFR's `REJECTED` assignment update and the comms
no-answer sweeper. This ask is only to **surface** them to the member.
