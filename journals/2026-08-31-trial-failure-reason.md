# 2026-08-31 — Trial: surface the decline reason (Innocent's #3 follow-up)

Innocent's backend review (#3): `convertMyTrial` now distinguishes a **decline**
(`status = "failed"` with a `failureReason`) from a charge **genuinely settling**
(`past_due`). Previously both came back as `past_due`, which is why a declined
card read to us as "pending".

## Change (both platforms)

- `TrialConversion` + the `convertMyTrial` query/wire type gained **`failureReason`**.
- `performConversion` already routed a non-`active`/non-`past_due` status to the
  charge-notice (so `failed` no longer polls as pending — that part was fixed with
  the settlement-signal correction). Now the notice shows **`failureReason`** ("Your
  card was declined.") instead of the generic "We couldn't confirm the payment."

## Files

- Swift: `Core/Network/AccountModels.swift` (+ wire type), `Core/Network/AsiApi.swift`
  (query + map), `Feature/Trial/TrialViewModel.swift`; test `TrialViewModelTests.swift`.
- Kotlin: `core/network/AccountModels.kt` (+ wire type), `core/network/AsiApi.kt`,
  `feature/trial/TrialViewModel.kt`; test `TrialViewModelTest.kt`.

## Tests

New `aFailedChargeShowsItsReasonAndDoesNotPend` / `a failed charge shows its reason
and does not pend`: `failed` + reason → step `chargeNotice`, error == the reason.

- Swift: `TrialViewModelTests` → **11 tests passed**.
- Kotlin: `TrialViewModelTest` → **BUILD SUCCESSFUL**.

## Not done here

`membershipEntitlement.conversionPending` (cold-start: a conversion mid-flight
when the app loads) — a separate enhancement to the Home/trial cold-load path,
noted for later.
