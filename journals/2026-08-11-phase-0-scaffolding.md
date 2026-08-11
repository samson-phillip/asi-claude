# 2026-08-11 — Phase 0: project scaffolding and design tokens

## Task
Start development. Scaffold `kotlin` and `swift` from greenfield, encode the
Attorney Shield design tokens on both platforms, and make the colour rules
enforceable by test rather than by review. Phase 0 of the development plan.

## Repos and files touched

**`kotlin`** (new project)
- `settings.gradle.kts`, `build.gradle.kts`, `gradle.properties`,
  `gradle/libs.versions.toml`, Gradle wrapper 8.12
- `app/build.gradle.kts` — compileSdk 35, minSdk 26, Compose
- `app/src/main/java/com/attorneyshield/member/core/design/` —
  `AsiColors.kt`, `AsiContrast.kt`, `AsiTheme.kt`, `AsiComponents.kt`
- `app/src/main/java/com/attorneyshield/member/MainActivity.kt`
- `app/src/test/.../AsiContrastTest.kt`, `PaletteAllowlistTest.kt`
- `AndroidManifest.xml`, `res/values/{strings,themes,colors}.xml`
- `README.md`, `.gitignore`

**`swift`** (new project)
- `AttorneyShield.xcodeproj/project.pbxproj` — hand-written, `objectVersion 77`
- `AttorneyShield/Core/Design/` — `AsiColors.swift`, `AsiContrast.swift`,
  `AsiTheme.swift`, `AsiComponents.swift`
- `AttorneyShield/AttorneyShieldApp.swift`
- `AttorneyShieldTests/` — `AsiContrastTests.swift`, `PaletteAllowlistTests.swift`
- `README.md`, `.gitignore`

**`asi-claude`** — this journal.

## Environment
JDK 17.0.10, Gradle 8.12, Android SDK (platform 35/36, build-tools 36),
Xcode 26.3 / Swift 6.2.4. Emulator `Pixel_8a_API_35`, simulator `iPhone 16 Pro`.

## Decisions and why

**Single-module Android, package-structured.** The plan calls for
`core/design`, `core/network`, `feature/*`. Those are packages for now rather
than Gradle modules — module extraction is cheap later and multi-module friction
is real now, while there is one screen.

**Colours modelled as data, not as platform colour types.** `AsiColor` on iOS
stores sRGB hex and computes `.swiftUI` at the point of use. This keeps the
contrast maths exact and unit-testable without a rendering context; going
through SwiftUI `Color` would have meant either UIKit round-trips or untestable
maths. Kotlin uses Compose `Color` directly since its channels are readable.

**`AsiContrast` lives in main, not test.** The palette contains real traps, so
the ratio needs to be assertable from anywhere — including at runtime, which the
Phase 0 smoke screen does.

**The app has no light scheme.** Shield Navy carries every reference frame, so
the dark scheme is pinned on both platforms rather than following the OS
setting. Android ignores `isSystemInDarkTheme`; iOS pins
`.preferredColorScheme(.dark)` and `UIUserInterfaceStyle = Dark`.

**Xcode project hand-written with synchronized folder groups.** XcodeGen and
Tuist are not installed, and installing tooling onto the machine seemed worse
than a project file that Xcode 16+ can maintain itself. `objectVersion 77`
means files added under `AttorneyShield/` join the target automatically — no
per-file registration, and no pbxproj merge conflicts when two people add files
at once.

**Inter is not bundled.** Licensing is still open (dev plan §9). Both platforms
map the brand weights onto the system face and build every style on a platform
text style, so Dynamic Type keeps working. Swapping the family in is a one-line
change in `AsiTheme`.

**Interim treatment for destructive actions.** `SecondaryButton` is the outlined
control used for hang-up until Blue Sky rules on an error colour. Nothing ships
in an unapproved value.

## API endpoints used
None. Phase 0 is tokens and harness only; networking is Phase 1.

## Test results

**Android — 20 tests, 0 failures, 0 skipped.**
`./gradlew :app:testDebugUnitTest` → BUILD SUCCESSFUL.
- `AsiContrastTest` 17 tests
- `PaletteAllowlistTest` 3 tests

**iOS — 21 tests, 0 failures.**
`xcodebuild test -scheme AttorneyShield -destination 'iPhone 16 Pro'` →
TEST SUCCEEDED.
- `AsiContrastTests` 17 tests
- `PaletteAllowlistTests` 4 tests

**Mutation-checked the gate rather than trusting it.** Flipping `ctaFg` from
Shield Navy to Pure White failed exactly two Android tests —
`CTA foreground clears AA on both golds` and `the CTA foreground is not white` —
and nothing else. Reverted and re-confirmed green. A test that cannot fail is
worth nothing, so this was worth the two minutes.

**Device verification.** Both apps installed and launched; screenshots captured.
The runtime ratios rendered on-screen match the test expectations exactly —
17.31, 7.03, 7.81, 5.53 — on both platforms, and the two builds are visually
indistinguishable apart from platform chrome. No crashes in logcat.

## Problems hit (worth not rediscovering)

**Homebrew's `gradle` runs on its own JDK.** `gradle wrapper` failed with an
error message whose entire body was `25.0.2`. That is Homebrew's bundled JDK 25,
which Gradle 8.12 does not support; no JDK 25 is installed system-wide.
`export JAVA_HOME=$(/usr/libexec/java_home -v 17)` fixes it. Documented in the
Android README because the error gives no clue.

**Two Compose compile errors, both mine:** `collectIsPressedAsState()` needs
`import androidx.compose.runtime.getValue` for `by` delegation, and
`TextGeometricTransform.None` is internal — it was a leftover and was deleted.

**Swift Testing's message parameter is `Comment`, not `String`.** It is
`ExpressibleByStringInterpolation` but not built from concatenation, so
`"msg" + array.joined()` fails to compile. Bind the string first, then
interpolate it.

## Open issues / next steps

1. **Phase 0 is not finished — the Vonage native spike remains.** The reference
   uses the *web* SDK; native needs the Vonage Video Android/iOS SDKs. Until the
   `apiKey`/`sessionId`/`token` triple is proven to connect natively, Phase 2
   estimates are not trustworthy. This is the next task.
2. **Android system nav bar renders light** under `enableEdgeToEdge()`, ignoring
   the theme's `navigationBarColor`. Cosmetic; fix when the real screens land.
3. No launcher icon yet on Android (`android:icon` removed so resource linking
   would pass). Needs the brand shield asset.
4. `member-client` still not stood up locally — needed before parity testing in
   Phase 2.
5. Blocking questions from the development plan §9 are still unanswered; none of
   them block Phase 1, which is networking and session against the documented
   API.
