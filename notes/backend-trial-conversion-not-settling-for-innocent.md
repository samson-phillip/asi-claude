# Trial conversion never leaves "trial" — backend investigation

**To:** Innocent
**From:** Mobile team
**Re:** A converted trial stays gated from the live attorney — the membership
never flips off `trial`

## Summary

A member converts their trial (`convertMyTrial`), the charge comes back
`past_due`, and even after the charge should have settled **and** a full
logout/login, the backend still reports the account as a **trial**. Every client —
both mobile apps and member-client — correctly keeps the live attorney gated,
because the gate is keyed on the membership status. So the member has paid (or
tried to) and can never reach what they paid for. This looks like a backend /
payment-settlement gap, not a client bug.

## What we see on the client

Log from the device:

```
[AsiTrial] convertMyTrial → org=6c53e00d-8682-11f1-a446-06cf81ac74a7
[AsiTrial] convertMyTrial ok · status=past_due alreadyConverted=false membership=trial
```

Then we read the account straight from the gateway (`myMembership` +
`membershipEntitlement`) **after logging out and back in** — so nothing is
cached client-side:

```
membership.statusCode = trial
entitlement.entitled  = true
entitlement.status    = trial
myAccountStatus (segmentation) = trial_member
```

The membership is **still `trial`**. It never transitioned to `active` (or any
paid status), and the entitlement status is still `trial` too.

## Why this gates the member (and why the client is right to)

The live-attorney gate — in member-client and mirrored in both mobile apps — is:

```
canConnectLive = entitled && !isTrialStatus(membership.statusCode)
isTrialStatus(s) = (s === "trial")
```

(`member-client/src/lib/trialGate.ts`.) With `statusCode === "trial"`,
`canConnectLive` is **false** no matter what the entitlement says — a trial is
always `entitled` (that is what gives a trial full app access), so the entitlement
cannot be the "converted" signal. **Only the membership leaving `trial` unlocks
the live attorney.** Until the backend flips it, member-client would gate this
account exactly as the mobile app does.

## What we need you to check

1. **Did the `past_due` charge actually settle?**
   `past_due` means the charge went onto an async rail (M-Pesa STK push / 3DS).
   For org `6c53e00d-8682-11f1-a446-06cf81ac74a7`, did that charge ever reach a
   settled/paid state on the PSP side, or is it still pending / did it fail? (If
   this is a dev sandbox where STK/3DS never actually settles, that alone explains
   it — and we should agree on how to test conversion end-to-end.)

2. **When a `past_due` trial conversion settles, does the settlement webhook flip
   the membership?** i.e. does `membership.status` move `trial → active` (and the
   entitlement status `trial → active`) when the PSP confirms payment? Please
   confirm the webhook handler updates the **membership status**, not only the
   invoice/payment row. This is the field every client reads.

3. **Is there a state where `entitled` is true but `status` stays `trial`
   indefinitely?** That is the exact state we captured. If it is expected, we need
   a different backend signal that means "converted" (see the question below).

## Questions

- What is the authoritative field/value that means **"this trial has converted to
  a paid membership"**? We are using `membership.statusCode !== "trial"`. If there
  is a better signal (e.g. a specific `status` value, or an
  `invoice.status === "paid"`), tell us and we will key on it.
- After a successful conversion, what should `membership.status` read —
  `active`? Something else?
- Is there a way to force a test conversion to settle in dev/uat so we can verify
  the full trial → paid → live-attorney path on device?

## What the mobile app does in the meantime

We have corrected the app so it no longer misleads the member:

- The conversion flow now reports **pending** (not "confirmed") until the
  membership actually leaves `trial`. Previously it confirmed on
  `entitlement.entitled`, which — as above — is always true for a trial, so it
  falsely said the charge had settled.
- The live-attorney gate keys on the membership status exactly like member-client.

So the app is now honest about the state, but it **cannot** unlock the live
attorney for an account the backend keeps as `trial`. That transition is yours.

Thanks,
Mobile team
