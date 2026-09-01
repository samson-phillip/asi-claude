# 2026-09-01 — Add card (33D), part 2b: iOS card entry lands + key diagnostic

## What unblocked iOS

Earlier the `stripe-ios` SwiftPM resolve wouldn't finish in this environment. It
completed this time — the checkout was already cached on disk (Samson had added
the package in Xcode; the source fetch that stalled before was warm now). With
the cache, `-resolvePackageDependencies` returned in seconds ("resolved source
packages: … Stripe …").

Note: the Xcode add hadn't persisted to `project.pbxproj` (git was clean), so I
re-added the SPM references in the project file myself — that's now the
authoritative integration. Anyone with a separate local Xcode package-add should
discard it to avoid a duplicate reference.

## iOS card entry (mirrors Android + member-client)

- `AddCardForm.swift`: Stripe's `STPPaymentCardTextField` wrapped for SwiftUI —
  the raw card / expiry / CVC / postal stay in Stripe's own field (PCI SAQ A).
  On Add it tokenises with `STPAPIClient.createPaymentMethod` → `pm_...` and hands
  only that to `attachCard`. **Tokenise only**, no SetupIntent confirm — the
  backend attaches, exactly like member-client and the Android side.
- `addCardPane` now dispatches on `addCardStatus`: `ready` → the form,
  `notConfigured` → the honest placeholder (empty publishable key),
  `loading/attaching` → spinner, `failed` → error + Try again.
- `open(.addCard)` now calls `prepareAddCard()` (it didn't before, which is why
  the iOS screen was still the static placeholder).
- SPM: added `StripePaymentsUI` + `StripePayments` products (pbxproj +
  `Package.resolved`).

## Diagnostic (both platforms)

`prepareAddCard` logs the resolved key so we can see on-device whether dev is
serving one — a publishable key is not a secret (it ships in the client), so the
length + `pk_test`-style prefix is safe to log:

- iOS: `print("[AsiAddCard] stripePublishableKey len=… prefix=…")`
- Android: `Log.i("AsiAddCard", "stripePublishableKey len=… prefix=…")`

**len=0** ⇒ Stripe isn't configured on dev (the query returns empty or errors) ⇒
the screen correctly shows the placeholder ⇒ that's the pending Innocent ask. A
non-zero `pk_test_…` ⇒ the real card form shows.

## Verification

- iOS: `** BUILD SUCCEEDED **` with the Stripe SDK; `AccountViewModelTests` →
  **46 passed**, `** TEST SUCCEEDED **`.
- Android: assembles with the SDK (part 2a); orchestration tests pass.

Both still need **on-device** verification with a real Stripe test card (the SDK
card field + tokenise + attach), and a **dev publishable key** behind
`stripePublishableKey` — until then the diagnostic will read `len=0` and the
placeholder is expected.

## Files

- Swift: `AttorneyShield.xcodeproj/project.pbxproj` + `Package.resolved`,
  `Feature/Account/AddCardForm.swift` (new), `Feature/Account/AccountScreen.swift`,
  `Feature/Account/AccountViewModel.swift`.
- Kotlin: `feature/account/AccountViewModel.kt` (diagnostic).
