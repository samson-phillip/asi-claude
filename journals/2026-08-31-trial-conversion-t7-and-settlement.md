# 2026-08-31 — Trial conversion: T7 processing UI + wait for settlement

## The report (with screenshots + logs)

Converting a trial to paid: (1) the processing screen didn't match the CodePen
T7, and (2) the success screen never came up. The log:

```
[AsiTrial] convertMyTrial ok · status=past_due alreadyConverted=false membership=trial
```

## Diagnosis

Two real issues, one shared root:

- **T7 didn't match the CodePen.** The reference T7 is: a gold **card-on-file
  badge**, "Processing your card on file…", "Confirming with Stripe — this takes
  a few seconds", an indeterminate bar, then "Visa •••• 4242 · Don't close the
  app" in a **gold-left-barred pill**. Our `processing` view had no icon, the card
  line was loose centred text, and the subtitle/bar were in the wrong order.

- **Success never showed.** `convertMyTrial` returns `past_due` — the charge is
  taken up on a rail that **settles a moment later** (3DS / M-Pesa STK; confirmed
  by member-client's own comment). Our flow mapped `past_due` straight to a
  terminal "Payment pending" and never re-checked. So T8 (`.confirmed`) was
  unreachable whenever the charge settled asynchronously.

member-client's *checkout* polls for exactly this (`publicSubscriptionStatus`
loop), and the CodePen's T7 copy ("takes a few seconds" → T8) assumes a brief
wait. The in-app flow just wasn't giving settlement that moment.

## Fix (both platforms)

1. **Rebuilt T7 to the reference** — gold card badge (navy-on-gold, R2), heading,
   subtitle, indeterminate bar, and the "· Don't close the app" line in the
   existing gold-barred pill (`trialFootnote` / `TrialFootnote`).
2. **Poll for settlement during T7.** On `past_due`, keep T7 on screen and poll
   the entitlement (5 × ~1.2s ≈ 6s). The moment `entitled` is true, refresh the
   membership and show **T8 confirmed**; only if it never clears do we fall back
   to the honest **pending** screen. Never claims coverage on a status that
   didn't actually activate.
   - swift: `TrialViewModel.awaitSettlement`; `settlementInterval` is an injected
     init param so tests skip the real wait.
   - kotlin: `TrialViewModel.awaitSettlement` (`delay` is virtual under
     `runTest`); `settlementIntervalMs` param.

## Files

- swift: `Feature/Trial/TrialFlow.swift` (T7 view), `Feature/Trial/TrialViewModel.swift`
  (poll). Tests: `TrialViewModelTests` — a past_due that settles → confirmed; one
  that never settles → pending.
- kotlin: `feature/trial/TrialSheets.kt` (T7 `ProcessingContent`, reusing
  `ic_row_card` + `TrialFootnote`), `feature/trial/TrialViewModel.kt` (poll).
  Same two tests.

## Test results

- **Android**: full `:app:testDebugUnitTest` — BUILD SUCCESSFUL.
- **iOS**: full `AttorneyShieldTests` — TEST SUCCEEDED.

## Honest caveat for the reporter

The poll gives an async-settling charge its few seconds and then shows T8. But if
the **dev backend leaves the subscription `past_due` indefinitely** (a test card
that never clears, or a missing settlement webhook), the app will still — correctly
— land on "Payment pending" after the window. In that case the membership genuinely
isn't active yet, and the remaining work is on the backend/Stripe side, not the
app. The screenshot's `membership=trial` alongside `status=past_due` is consistent
with "charge initiated, not yet cleared."
