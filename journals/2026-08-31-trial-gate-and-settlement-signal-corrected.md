# 2026-08-31 — Trial gate + settlement signal, corrected

## Report

Follow-up to `2026-08-31-trial-gate-reopens-after-conversion.md`. The member
logged out and back in; Home still showed **"Active · 24/7 coverage"** but tapping
**Make a call** still opened **"You're on a Trial"** and asked for payment. Logs:

```
[AsiTrial] convertMyTrial → org=6c53e00d-…
[AsiTrial] convertMyTrial ok · status=past_due alreadyConverted=false membership=trial
[AsiTrial] settlement confirmed after poll
```

## What the earlier fix got wrong

The earlier fix keyed `isTrial` on `entitlement.status == "active"` → "not a
trial", on the assumption that a conversion flips the entitlement to `active`
while the membership lags. **A gate diagnostic on the live account proved that
assumption false.** After conversion + settlement + a full re-login the backend
still returns:

```
seg=trial_member  membership.statusCode=trial  ent.entitled=true  ent.status=trial
```

So the entitlement never becomes `active` here — it stays `trial` and stays
`entitled`. The earlier on-sim "A/B" only passed because it *forced*
`entitlement.status = active`, a state this backend does not produce. That
verification checked a fiction.

## The actual truth

The account is **genuinely still a trial** on the backend — `membership.statusCode`
never left `"trial"`. member-client gates the live call on exactly this
(`canConnectLive = entitled && !isTrialStatus(statusCode)`, `isTrialStatus === "trial"`),
so **member-client would gate it identically.** The trial modal is *correct*.

Two real defects sat underneath:

1. **The false "settlement confirmed".** `awaitSettlement` / `recheckSettlement`
   confirmed on `entitlement.entitled` — but a trial is **always** entitled (full
   app access is the whole point of a trial). So the poll reported success the
   instant it ran, for a `past_due` charge that had not settled and a membership
   still reading `trial`. That is the log line above, and it is what made the
   member believe they had converted.

2. **The gate keyed on the wrong signal.** `entitlement.status == "active"` is not
   a signal this backend emits for a converted trial; the check was inert here and
   wrong in principle (it would un-gate a still-`trial` membership the moment its
   entitlement read `active`, the exact #136 leak).

## Fix (both platforms)

- **Gate** — `isTrial` now keys on the **membership status** only
  (`membership.isTrial`), with the `trial_member` segmentation as the fallback for
  a not-yet-loaded membership. Removed the `entitlement.status == "active"`
  escape. This is member-client's `isTrialStatus`/`canConnectLive` exactly: only
  the membership leaving `"trial"` un-gates the live attorney.
- **Settlement** — `awaitSettlement` / `recheckSettlement` now confirm on
  member-client's `canConnectLive` signal: `entitled && membership has left "trial"`
  (a shared `refreshAndCheckConverted` reads both). A `past_due` that never clears
  correctly stays **pending** instead of falsely reporting **confirmed**.

## Files

- `swift/.../Home/HomeViewModel.swift` (gate), `swift/.../Trial/TrialViewModel.swift`
  (settlement); `kotlin/.../home/HomeViewModel.kt`, `kotlin/.../trial/TrialViewModel.kt`.
- Tests: `AccountGateTests.swift` / `HomeViewModelTest.kt` — replaced the
  wrong "converted trial not gated (entitlement active)" case with two correct
  ones: an **entitled trial stays gated** until the membership flips, and a trial
  whose **membership has actually left "trial"** is no longer gated. Existing
  settlement tests already stubbed both membership + entitlement, so they cover the
  new two-signal confirm.

## Tests

- Swift: `AccountGateTests` + `TrialViewModelTests` + `HomeViewModelTests` →
  **40 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `HomeViewModelTest` + `TrialViewModelTest` → **BUILD SUCCESSFUL**.

Diagnostic logging removed; clean build reinstalled on the sim.

## ⚠️ Upstream — for Innocent / backend

The mobile app cannot make this account non-trial: the backend still has
`membership.statusCode = "trial"` and `entitlement.status = "trial"` after a
`past_due` conversion and a re-login. `past_due` is an async rail (M-Pesa STK /
3DS) that must settle server-side to flip the membership. Either the charge never
actually settled (STK not approved / dev sandbox) or the settlement webhook is not
flipping the membership. **The conversion completing is a backend/payment matter,
not a mobile one** — the app now reports it honestly (pending, gated) instead of
claiming success.

## Note to self

Verify against the *real* backing state, not a forced one. The first fix's on-sim
A/B injected the state it wanted to see; a gate diagnostic on the actual account
would have shown `ent.status = trial` immediately and saved the round trip.
