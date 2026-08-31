# 2026-08-31 — Home profile icon opens the profile screen, not sign-out

## Bug

Tapping the person icon in the Home top-right **signed the member out** — a
surprising, destructive action for what looks like a "go to my profile" button.

## Fix

The icon now opens the **profile (Account) screen** — which is exactly where the
bottom "Profile" tab already points (`Destination.Account` / `.account`, labelled
"Profile"). Sign-out already lives *inside* that screen, so it is still one tap
away, just not on a stray tap of the corner icon.

- Renamed the Home callback `onSignOut` → `onOpenAccount` on both platforms; the
  icon's action and accessibility label change from "Account and sign out" to
  "Profile".
- Rewired the app: Home's icon now navigates to the Account destination instead of
  calling `session.signOut()`. The Account screen's own sign-out is untouched.

## Files

- Swift: `Feature/Home/HomeScreen.swift` (button + label + param),
  `AttorneyShieldApp.swift` (wiring).
- Kotlin: `feature/home/HomeScreen.kt` (button + label + param + preview),
  `MainActivity.kt` (wiring).

## Verification

Both build clean; no test referenced the old callback or label. Could not
screenshot on the sim (its session had ended — sitting at the login screen — and
signing in needs credentials we don't use on the sim). The change is a
callback rename + a nav target swap, so risk is low; eyeball once logged in:
tapping the top-right person icon should open Profile/Account, and sign-out should
still be reachable from inside that screen.
