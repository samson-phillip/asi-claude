# 2026-09-01 — Add card: Android crash opening the card form (theme)

## Crash

Opening Add card on Android crashed instantly:

```
android.view.InflateException: … layout/stripe_card_input_widget:
  Error inflating class com.google.android.material.textfield.TextInputLayout
Caused by: java.lang.IllegalArgumentException: The style on this component
  requires your app theme to be Theme.AppCompat (or a descendant).
  … com.stripe.android.view.CardInputWidget.<init>
  … AddCardForm(AddCardForm.kt:55)
```

(The diagnostic log fired first — `stripePublishableKey len=107 prefix=pk_test_` —
so dev's key and the `Ready` state were fine; the crash was purely the widget.)

## Cause

Stripe's `CardInputWidget` inflates Material `TextInputLayout`s, which enforce an
**AppCompat / MaterialComponents** theme on their host `Context`. The app's window
theme (`Theme.AttorneyShield`) extends **`android:Theme.Material.NoActionBar`** —
the *platform* Material theme, **not** an AppCompat descendant (the app is Compose,
so its real theming is in `AsiTheme`, and the XML theme only sets the navy window
background). So `LocalContext.current` handed the widget an incompatible theme.

## Fix

Host the widget in a MaterialComponents-themed context:

- `res/values/themes.xml`: a new
  `Theme.AttorneyShield.CardInput` extending `Theme.MaterialComponents.DayNight`
  (DayNight so it follows the same light/dark as Compose). The parent resolves via
  resource merging — the Material Views library is already on the classpath
  transitively through Stripe, so **no new dependency**.
- `AddCardForm.kt`: create the widget with
  `CardInputWidget(ContextThemeWrapper(context, R.style.Theme_AttorneyShield_CardInput))`.

(Same `ContextThemeWrapper` trick already used for the DOB `NumberPicker` wheels —
legacy Android Views hosted in Compose need a compatible theme handed in.)

iOS is unaffected — `STPPaymentCardTextField` is a plain UIKit view with no
theme-inflation requirement (already confirmed tokenising on device).

## Verification

- Android: `assembleDebug` green (the `Theme.MaterialComponents.DayNight` parent
  merged fine — no AAPT error). Needs the on-device re-check that the form now
  opens and a test card adds.

## Second crash (after the theme fix): PaymentConfiguration

With the theme fixed the widget inflated, then crashed on a background thread:

```
IllegalStateException: PaymentConfiguration was not initialized. Call PaymentConfiguration.init().
  … CardWidgetViewModel … determineCbcEligibility
```

`CardInputWidget` launches a card-brand-choice eligibility check that reads the
global `PaymentConfiguration`; the `Stripe(context, key)` constructor didn't set
it up in time. Fix: call `PaymentConfiguration.init(context, publishableKey)`
before creating the widget (in a `remember(publishableKey)` at the top of the
form, so it runs once, before the `Stripe` instance and the widget). iOS has no
equivalent — `STPAPIClient(publishableKey:)` is self-contained.

## Files

- Kotlin: `res/values/themes.xml`, `feature/account/AddCardForm.kt` (theme wrap +
  `PaymentConfiguration.init`).
