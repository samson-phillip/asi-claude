# 2026-09-01 — iOS: white-ground app icon + a real launch screen

Two branding fixes, both driven off the official shield
(`asi-gold-logo.png`, confirmed identical to `brand_shield_hero.svg`).

## 1. App icon on a white ground

The navy icon read as "black" in the App Store Connect build list (7.3(3)),
where the prior production builds were the shield on **white**. The user asked
for a white background.

Caveat found: the shield's **outer border is white/cream** (it's designed to
frame against a *dark* ground), so on a plain white background the left border
vanishes and the mark looks lopsided. Fix: give the outer shield a **navy
border** on white — navy + gold are the brand's two colours, so the shield now
reads as a crisp, symmetric, framed gold mark on white. Rebuilt the composed SVG,
rasterised with `qlmanage`, flattened RGBA→RGB (no alpha).

- `AppIcon-1024.png` regenerated (white ground, navy-bordered gold shield).

## 2. Launch screen (was blank)

The project had `INFOPLIST_KEY_UILaunchScreen_Generation = YES`, which generates
an **empty** launch screen — hence "the splash screen doesn't show." There was no
storyboard or launch image at all.

Added a branded launch screen:
- `Resources/LaunchScreen.storyboard` — Shield Navy (`#0D1B2E`) ground, the shield
  centred (140×156 pt, aspect-fit, auto-layout centred) so it adapts to every
  iPhone/iPad size.
- `Resources/Media.xcassets/LaunchLogo.imageset` — the shield on transparent,
  built from `asi-gold-logo.png` (tight-cropped, 660 px tall on a 720² canvas).
- Build setting swap on both app configs: dropped
  `INFOPLIST_KEY_UILaunchScreen_Generation`, added
  `INFOPLIST_KEY_UILaunchStoryboardName = LaunchScreen`.

No pbxproj file wiring needed for the new files: the project uses Xcode 16
**synchronized folder groups** (`PBXFileSystemSynchronizedRootGroup`), so anything
under `AttorneyShield/` is compiled automatically.

## Verify / build

- `** BUILD SUCCEEDED **`. Confirmed in the built `.app`: `LaunchScreen.storyboardc`
  present, `UILaunchStoryboardName = LaunchScreen` in `Info.plist`, `LaunchLogo`
  in `Assets.car`; the icon PNG has no alpha.
- Launch screens are **cached** by iOS/Simulator — delete the app / erase the
  simulator to see the new splash on next run.

## Files

- `swift/AttorneyShield/Resources/Media.xcassets/AppIcon.appiconset/AppIcon-1024.png`
- `swift/AttorneyShield/Resources/LaunchScreen.storyboard`
- `swift/AttorneyShield/Resources/Media.xcassets/LaunchLogo.imageset/{launch_logo.png,Contents.json}`
- `swift/AttorneyShield.xcodeproj/project.pbxproj`
