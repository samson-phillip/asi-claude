# 2026-08-31 — Trial gate reopens after a successful conversion

## Report

After converting a trial to a paid account, the success screen shows and Home
reads **"Active · 24/7 coverage"** — but tapping **Make a call** re-opens the V2
trial modal (the "start your trial / convert" sheet), as if the member were still
on a trial. Screenshots `1st.png` / `2nd.png`: success confirmed, yet the connect
path still gates as trial.

Logs confirmed the charge actually cleared:

```
[AsiTrial] convertMyTrial → org=… ok · status=past_due alreadyConverted=false membership=trial
[AsiTrial] settlement confirmed after poll
```

So the entitlement settled (past_due rail → confirmed), but the connect gate kept
treating the account as a trial.

## Root cause

`AccountGate.isTrial` (screen 35 gate) ORed **two** signals:

```
membership?.isTrial == true  ||  accountStatusCode == "trial_member"
```

`accountStatusCode` is the `myAccountStatus` **segmentation**, carried from the
session. It is set **once at sign-in and never re-fetched** — `refreshMembership()`
/ `loadAccount()` update the membership and entitlement, but not the segmentation.
So after conversion it still reads `trial_member`, the OR stays true, and the gate
re-opens the trial modal even though the money side (entitlement/membership) has
moved on.

member-client does **not** do this: its live-call gate keys off the membership
status (`isTrialStatus(statusCode)`), never the segmentation. The segmentation was
only ever meant as a fallback for a *freshly-created* trial whose membership row
hasn't landed yet.

## Fix

Make the money the authority; use segmentation only as a fallback when there is no
membership yet, and let a definitively **active** entitlement veto the trial state
outright (covers the window right after conversion where the membership status
string can still lag behind the entitlement):

```
if entitlement.status == "active" → not a trial
else if membership present        → membership.isTrial
else                              → segmentation == "trial_member"
```

- A converted member (active entitlement, segmentation still `trial_member`) is
  **no longer** gated — `Make a call` goes straight to the connect tray.
- A freshly-created trial with no membership row yet is **still** gated on the
  segmentation alone — the original reason that fallback exists is preserved.

## Files

- `swift/AttorneyShield/Feature/Home/HomeViewModel.swift` — `AccountGate.isTrial`.
- `kotlin/app/.../feature/home/HomeViewModel.kt` — `HomeUiState.isTrial` (mirror).

Both keep the same three-way precedence and the same KDoc/doc-comment explaining
why segmentation is a fallback, not an authority.

## Tests

Added a matching pair on each platform:

- **`aConvertedTrialIsNotGatedEvenWhileSegmentationLags`** — active entitlement +
  `trial_member` segmentation + `trial` membership ⇒ `!isTrial` and `canCall`.
- **`aFreshTrialWithNoMembershipYetIsStillGated`** — `trial_member` segmentation,
  no membership ⇒ `isTrial`.

The existing trial-gate tests (segmentation-alone gates, membership-status gates,
never-mistaken-for-expired) are unchanged and still pass.

- Swift: `xcodebuild test … -only-testing:AccountGateTests
  -only-testing:HomeViewModelTests` (single-process, iPhone 16 Pro) →
  **28 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `./gradlew testDebugUnitTest --tests …HomeViewModelTest` →
  **BUILD SUCCESSFUL**.

## Note

The segmentation staleness is real but out of scope here — the correct long-term
fix would be to re-fetch `myAccountStatus` after a conversion (or drop the
segmentation from the gate entirely once membership is trusted). This change makes
the gate correct regardless, by trusting the money over the stale segmentation.
