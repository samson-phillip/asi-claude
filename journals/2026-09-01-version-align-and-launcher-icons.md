# 2026-09-01 — Align iOS version to 2.0.0/127 + add launcher icons

## Version

iOS was on the Xcode defaults (`MARKETING_VERSION 0.1.0`, app/test targets
`1.0`); Android was already `2.0.0 (127)`. Set **all** iOS targets to
`MARKETING_VERSION = 2.0.0`, `CURRENT_PROJECT_VERSION = 127` in `project.pbxproj`
so Settings reads "Version 2.0.0 (127)" on both platforms.

## Launcher icons

Both apps had **no** app icon (system default). Built a branded icon from the
existing shield artwork on Shield Navy (`#0D1B2E`):

- **iOS:** generated a 1024×1024 `AppIcon-1024.png` (navy ground + the
  `brand_shield.png` composited and **flattened — no alpha**, as Apple requires)
  with PIL, added `Media.xcassets/AppIcon.appiconset` (single-size, modern Xcode
  auto-derives the rest), and set `ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon`
  on the app target's Debug + Release configs.
- **Android:** an **adaptive icon** (no PNG needed at minSdk 26). `mipmap-anydpi-v26/
  ic_launcher.xml` (+ `ic_launcher_round.xml`): `<background>` =
  `@color/asi_bg_primary` (navy), `<foreground>` = `ic_launcher_foreground.xml` —
  a layer-list that centres the existing `ic_brand_shield` **vector** at its own
  88:100 aspect (52×59dp) inside the safe zone (no stretch). Wired
  `android:icon`/`android:roundIcon` into the manifest `<application>`.

Both icons are the brand shield on navy — a clean, on-brand mark derived from the
same shield the app already draws; a bespoke designed icon can replace them later
without any wiring changes.

## Verification

- Android: `assembleDebug` green (adaptive icon + `@color` background merged fine).
- iOS: `** BUILD SUCCEEDED **` (AppIcon compiled from the 1024 png).

Both want an on-device / launcher glance to confirm the icon renders (and, on
Android, sits well within the round/squircle mask).

## Files

- Swift: `AttorneyShield.xcodeproj/project.pbxproj`,
  `Resources/Media.xcassets/AppIcon.appiconset/{AppIcon-1024.png,Contents.json}`.
- Kotlin: `AndroidManifest.xml`, `res/drawable/ic_launcher_foreground.xml`,
  `res/mipmap-anydpi-v26/ic_launcher.xml` + `ic_launcher_round.xml`.
