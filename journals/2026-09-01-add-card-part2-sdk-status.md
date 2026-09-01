# 2026-09-01 — Add card (33D), part 2: Stripe SDK — Android done, iOS blocked here

## Where it landed

- **Android — done** (committed, assembled). Added `com.stripe:stripe-android`
  (`20.53.0`; Maven resolved cleanly, no Compose conflict, full `assembleDebug`
  green). `AddCardForm` hosts Stripe's own `CardInputWidget` (raw card stays in
  Stripe's view — PCI SAQ A) and tokenises via `Stripe.createPaymentMethod` →
  `pm_...`; only the token leaves the screen, handed to the VM's `attachCard`.
  `AddCardPane` dispatches on `addCardStatus`: `Ready` → the form,
  `NotConfigured` → the honest placeholder (empty publishable key),
  `Loading/Attaching` → spinner, `Failed` → error + retry.
- **iOS — foundation done (committed), SDK/UI blocked in THIS environment.**

## The iOS block (environment, not code)

I added the `stripe-ios` SwiftPM package to `project.pbxproj` (mirroring the
Lottie/Vonage entries: package reference + `StripePaymentsUI`/`StripePayments`
product deps + build-file links). But `xcodebuild -resolvePackageDependencies`
**never completed** — after many minutes stripe-ios was still not fetched (no
checkout, absent from `Package.resolved`). Our own git over HTTPS works
(pull/push all fine), but resolving stripe-ios's large transitive dependency tree
stalled here. Rather than leave the iOS project half-resolved or block
indefinitely, I **reverted the `.pbxproj`** — iOS is back on the committed,
building foundation. No broken state.

This is an environment limitation (SPM fetch of a heavy SDK), **not** a design or
code problem: the exact same integration is trivial in Xcode or CI with normal
package access.

## iOS — the remaining step (small, well-specified)

1. In Xcode: **File → Add Package Dependencies →**
   `https://github.com/stripe/stripe-ios` → add **StripePaymentsUI** (+
   **StripePayments**). (Or let CI resolve it — the `.pbxproj` edit is known and
   was reverted only because it couldn't resolve here.)
2. Add a `DocumentViewer`-style card sheet mirroring Android's `AddCardForm`:
   an `STPPaymentCardTextField` (UIViewRepresentable) → on Add,
   `STPAPIClient(publishableKey:).createPaymentMethod(with: STPPaymentMethodParams(card: field.cardParams, …))`
   → `paymentMethod.stripeId` → `model.attachCard(paymentMethodId:setAsDefault:)`.
   Tokenise only (no SetupIntent confirm), exactly like Android/member-client.
3. Present it from the Add-card pane when `addCardStatus == .ready(key)`; keep the
   `.notConfigured` placeholder otherwise.

Everything it calls — `prepareAddCard`, `attachCard`, the three backend
mutations — is already in place and unit-tested (part 1).

## For the team

- **Add card works end-to-end on Android** once the backend serves a Stripe
  **publishable key** on dev behind `stripePublishableKey` (empty today → the
  screen shows the placeholder, by design). Confirm with Innocent whether dev has
  a Stripe test key configured.
- Both platforms still need **on-device verification** with a real test card
  (tokenisation + attach + the card appearing in the list) — unit tests cover the
  backend flow, not the SDK card field.

## Files (this part)

- Kotlin (committed): `app/build.gradle.kts`, `gradle/libs.versions.toml`,
  `feature/account/AddCardForm.kt` (new), `feature/account/AccountScreen.kt`,
  `feature/account/AccountViewModel.kt` (open→prepare), `MainActivity.kt`.
- Swift: no part-2 changes retained (SPM add reverted; foundation from part 1
  stands).
