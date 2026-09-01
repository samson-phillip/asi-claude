# 2026-09-01 — Home shows the previous account after switching (stale VMs)

## Bug

On Android, signing out of `x1@…` and into the paid `x2@…` left **Home
reflecting `x1`'s state** (greeting, coverage). A shared-phone / re-login
correctness (and privacy) bug.

## Cause — ViewModels outlive the session

Both apps create their feature view models **once** and keep them for the whole
app run, so a new sign-in inherits the previous account's cached state:

- **Android:** every VM is `viewModel(factory = …)` — scoped to the Activity's
  `ViewModelStore`. `SessionManager.signOut()` clears the token/member/store but
  **never the ViewModelStore**, so `HomeViewModel` (greeting set at construction,
  plus cached membership/entitlement) survives sign-out.
- **iOS:** every VM is a `@State` built in the app's `init` — created once,
  never rebuilt. `HomeViewModel.greetingName` is set only in `init` and `load()`
  never updates it, so after a switch Home showed the previous member's name.

## Fix — fresh account-scoped VMs when the member changes

- **Android** (`MainActivity`): a `LaunchedEffect(signedInMember == null)` that
  clears `LocalViewModelStoreOwner.current.viewModelStore` when the session ends.
  That's exactly the store `viewModel()` reads from, so the next sign-in builds
  every feature VM fresh. All sign-out paths (sign-out, account close, server
  kick → member `null`) navigate to an unauthed screen first, so nothing
  account-scoped is composed when it clears.
- **iOS** (`AttorneyShieldApp`): an `.onChange(of: session.member?.userId)` that
  rebuilds the account-scoped view models (`home`, `account`, `glovebox`,
  `activity`, `notifications`, `situations`, `trial`, `setup`, `completion`) —
  `login` is left alone since it owns the sign-in that drives the change. Stored
  the shared nudge/step store at its concrete type so the inits can be
  reconstructed.

## Verification

- Android: `assembleDebug` green.
- iOS: `** BUILD SUCCEEDED **`.

Both still want an on-device re-check: sign in as `x1`, sign out, sign in as
`x2`, and confirm Home (greeting + coverage), Account, and Glovebox all show
`x2`.

## Files

- Kotlin: `MainActivity.kt`.
- Swift: `AttorneyShieldApp.swift`.
