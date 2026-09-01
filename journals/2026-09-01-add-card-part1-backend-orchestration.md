# 2026-09-01 — Add card (33D), part 1: backend + orchestration

## Context

Reversing the earlier "can't be built" framing. member-client has a working
`AddPaymentMethodScreen`; the backend exposes everything; the CodePen has the UI.
The only real gap was that the native apps lack **client-side card tokenisation**,
which by PCI must go through Stripe's SDK. This part lands the SDK-independent
foundation (safe, tested); the Stripe SDK + card entry is part 2.

## How member-client actually does it (the contract we mirror)

`getStripePublishableKey` → mount Stripe Elements → **tokenise only**
(`stripe.createPaymentMethod` → `pm_...`, the raw card never touching app JS) →
best-effort `createSetupIntent` handshake → `attachPaymentMethod(providerRef:
pm_...)`. It does **not** confirm the SetupIntent client-side (so we won't use
PaymentSheet, which would).

## This part

- **`AsiApi` (both platforms):** `stripePublishableKey()` (empty = not configured
  → placeholder), `createSetupIntent(org, name, email)`, and
  `attachPaymentMethod(org, pm, setDefault, name, email)` — exact mirrors of the
  member-client mutations (`CreateSetupIntentInput` / `AttachPaymentMethodInput`).
- **`AccountViewModel` (both platforms):** the testable orchestration —
  - `prepareAddCard()` → resolves the key; empty → `NotConfigured` (the honest
    placeholder), else `Ready(publishableKey)`.
  - `attachCard(pm, setAsDefault)` → best-effort setup-intent, then attach (first
    card forced default), then reload the card list and return to the
    payment-methods pane with "Card added."; failures surface as `Failed(reason)`.
  The Stripe SDK presentation stays in the view (part 2); the VM owns only the
  backend flow, so it's unit-tested end to end.

## Files

- Swift: `Core/Network/AccountModels.swift`, `Core/Network/AsiApi.swift`,
  `Feature/Account/AccountViewModel.swift`; test `AccountViewModelTests.swift`.
- Kotlin: `core/network/AccountModels.kt`, `core/network/AsiApi.kt`,
  `feature/account/AccountViewModel.kt`; test `AccountViewModelTest.kt`.

## Tests

Both platforms: an empty publishable key → placeholder; a configured key →
ready; a tokenised card attaches, refreshes the list, and returns to the pane
with a confirmation; a failed attach surfaces the error.

- Swift: `AccountViewModelTests` → **46 passed**, `** TEST SUCCEEDED **`.
- Kotlin: `AccountViewModelTest` → **BUILD SUCCESSFUL**.

## Next (part 2)

Add `stripe-ios` (SPM) + `com.stripe:stripe-android` (Maven has 23.17.1;
compileSdk 35), implement the card entry (Stripe card field → `createPaymentMethod`
→ `pm_...`, tokenise only), wire it to `attachCard`, keep the `NotConfigured`
placeholder. The dependency add is the one real risk; if it can't resolve/compile
cleanly it gets reverted, leaving this tested foundation intact.
