# 2026-09-01 — App Store upload rejected: dropped iPad support

## Error

Upload validation:

> This bundle does not support one or more of the devices supported by the
> previous app version. Your app update must continue to support all devices
> previously supported. You declare supported devices in Xcode with the Targeted
> Device Family build setting. (QA1623)

## Cause

The app target was `TARGETED_DEVICE_FAMILY = 1` (iPhone only). The previous App
Store version (the old Expo/React-Native app) was **Universal** (`1,2` —
iPhone + iPad). Apple does not allow an update to *drop* a device family the
prior version supported, so an iPhone-only bundle is rejected.

## Fix (`swift`, `project.pbxproj`, app target Debug + Release only)

- `TARGETED_DEVICE_FAMILY = "1,2"` — restores iPad support.
- `INFOPLIST_KEY_UIRequiresFullScreen = YES` — the app is portrait-only
  (`UISupportedInterfaceOrientations = …Portrait`). An iPad app that does **not**
  require fullscreen must support *all* orientations (the multitasking rule);
  requiring fullscreen lets it stay portrait-only on iPad and pre-empts that as
  the next validation failure.

Test / UITest targets left at family `1` — they are not uploaded.

The app now runs on iPad as a portrait, fullscreen build (the phone SwiftUI
layout at iPad size). That is enough to ship / TestFlight; bespoke iPad layouts
can come later if wanted.

## Verify / build

- `** BUILD SUCCEEDED **` (pbxproj edit valid, made with a whitespace-safe script
  so only the two app configs changed).

## Watch on the next upload (not changed — the user's call)

- App target is `MARKETING_VERSION = 7.3`, `CURRENT_PROJECT_VERSION = 1` (the
  test targets still read 2.0.0 / 127 — cosmetic, they don't ship). If a 7.3
  build was already uploaded, the build number will need to climb above the last
  one; a fresh marketing version starting at build 1 is otherwise fine.
- Deployment target is iOS 17.0. If the previous version supported an older iOS,
  a separate "minimum OS" validation could appear — distinct from this device
  family one. Not seen yet.
- App Store Connect will likely want **iPad screenshots** now that the binary is
  Universal.

## Files

- `swift/AttorneyShield.xcodeproj/project.pbxproj`
