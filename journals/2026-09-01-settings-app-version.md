# 2026-09-01 — Show the app version on Settings

Small request: display the app version on the Settings screen (33C).

## Change

A centred, muted version line at the bottom of Settings, under the "Delete
account lives in Plan Details" footnote:

- **Android:** read from the package at runtime (`PackageManager.getPackageInfo`)
  — no `BuildConfig` needed (it isn't enabled). Shows `Version <versionName>
  (<versionCode>)`, e.g. `Version 2.0.0-debug (127)` on debug, `Version 2.0.0
  (127)` on release. `longVersionCode` guarded for API < 28.
- **iOS:** from `Bundle.main.infoDictionary` — `CFBundleShortVersionString`
  (MARKETING_VERSION) + `CFBundleVersion` (build). Shows `Version <x> (<build>)`.

## Version mismatch flagged

The two platforms carry **different** marketing versions: Android
`versionName 2.0.0` (matching the shipping app / "ASI 2.0"), iOS
`MARKETING_VERSION 0.1.0` (a leftover Xcode default). So iOS Settings currently
reads "Version 0.1.0 (1)". Recommend bumping iOS MARKETING_VERSION to `2.0.0`
(and CURRENT_PROJECT_VERSION as desired) to match — a one-line project change,
left for a release decision rather than done unilaterally.

## Verification

- Android: `compileDebugKotlin` green.
- iOS: `** BUILD SUCCEEDED **`.

## Files

- Kotlin: `feature/account/AccountScreen.kt` (`SettingsPane`).
- Swift: `Feature/Account/AccountScreen.swift` (`settingsPane` + `appVersion`).
