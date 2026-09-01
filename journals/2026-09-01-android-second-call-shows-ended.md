# 2026-09-01 — Android: second call shows "Call ended" instead of connecting

## Symptom

On Android, after finishing one call, starting another (same incident type +
attorney) jumped straight to the **"Call ended / You're covered / Your session has
ended"** screen instead of connecting.

## Cause

The call screen's `CallViewModel` is created with `viewModel(key = ...)`, keyed
`"call-${type.id}-${attorneyId}"`. A `viewModel()` with a given key returns the
**retained** instance from the Activity's ViewModelStore. A second call to the
same type + attorney produced the **same key**, so it reused the first call's view
model — which was already in its `CallEnded` phase — and the screen rendered the
ended state immediately.

(`CallViewModel.init { start() }`, so a *fresh* VM connects fine; the bug was
purely that the second attempt got a stale one.)

## Fix (`kotlin`, `MainActivity.kt`)

Give every call attempt a unique nonce so the key differs each time and
`viewModel()` builds a fresh VM (which then `start()`s a new call):

- `PendingCall` gained a `nonce: Int`.
- A `callNonce` counter at the app root is bumped in `begin()` and passed into
  `PendingCall`.
- The call view-model key is now `"call-${call.nonce}"`.

This mirrors iOS, which was already correct — its `begin()` always reassigns
`call = CallViewModel(...)`, a brand-new instance per call, so it never had this
bug. **iOS unchanged.**

## Verify

- `compileDebugKotlin` **BUILD SUCCESSFUL**.
- On-device: place a call, end it, place another (same type/attorney) — it should
  now connect rather than show the ended screen.

## Files

- `kotlin/app/src/main/java/com/attorneyshield/member/MainActivity.kt`
