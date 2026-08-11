# 2026-08-11 — Phase 4: hardening

## Task
Rotation and state loss, dynamic type, offline behaviour, and token-expiry
handling. Correctness first, polish second.

## Repos and files touched

**`kotlin`** — `core/network/AsiApi.kt` (`OfflineException`,
`UnauthorizedException`), `core/session/SessionManager.kt` (`onUnauthorized`),
`feature/home/HomeViewModel.kt`, `MainActivity.kt` (saveable navigation),
`AndroidManifest.xml` (portrait lock), `feature/welcome/WelcomeScreen.kt`
(scrollable pages), tests `AsiApiTest.kt` (+5),
`androidTest/feature/DynamicTypeTest.kt` (new, 5).

**`swift`** — `Core/Network/AsiApi.swift` (`OfflineError`, `UnauthorizedError`,
`isOffline`), `Core/Session/SessionManager.swift`,
`Feature/Home/HomeViewModel.swift`, `Feature/Welcome/WelcomeScreen.swift`
(scrollable pages), `Core/Design/AsiComponents.swift` (wordmark scaling cap),
tests `AsiApiTests.swift` (+4).

## Two real defects found, both by looking rather than by test

### 1. Activity recreation threw a signed-in member back to Welcome

Navigation state was in `remember`, not `rememberSaveable`. Verified on device:
navigating to Login by tap and then rotating landed back on **Welcome**.

Rotation is only one trigger. An **appearance switch**, a font-size change and a
locale change all recreate the activity too — so this would have hit anyone
toggling dark mode mid-flow, not just anyone rotating.

Fixed two ways:
- Navigation is `rememberSaveable`. Re-verified on device: both rotation and a
  dark/light switch now hold the destination.
- **Portrait locked**, matching iOS (already portrait-only) and the reference,
  whose frames are all portrait. This also removes rotation as a way to destroy a
  call mid-encounter.

A recreated `Call` destination deliberately resolves to Home rather than trying
to resume: the media session, camera and socket left with the old activity, so
pretending otherwise would show a dead call screen.

**The portrait lock is a deliberate accessibility trade-off** — someone who
mounts their phone in landscape now cannot. Recorded in `open-concerns.md`;
revisit if that matters more than call stability.

### 2. The welcome carousel clipped its own body copy at large text

At 2× font scale the last line of every page's body was cut off — "encounter.
Available 24/7" and then nothing. A member using large text simply could not read
the end of each sentence. The pager page had a fixed height and no scroll.

Fixed on both platforms by making each page scrollable. Login was already fine.
The live call screen and the 409 retry path were checked and also fine — their
controls stay reachable at 2×, which matters most since a member cannot scroll
away from a live call.

`DynamicTypeTest` now gates this at **2.0** scale, beyond the standard slider and
into the accessibility range: `performScrollTo` fails outright if the node is not
inside a scrollable container, so it asserts both existence and reachability.

Also capped the **wordmark**'s scaling on iOS. A brand lockup is not content; left
uncapped it wrapped to two lines at the accessibility sizes and dragged the shield
out of alignment. The screen's actual content still scales freely.

## Offline and expiry now say something useful

Both were previously surfacing raw plumbing. Two new error types on each platform:

- **Offline** — "You appear to be offline. Check your connection and try again."
  The platform's own message is `Unable to resolve host …` / `Failed to connect`,
  which is true and useless to someone at the roadside.
- **Unauthorized (401/403)** — "Your session has expired. Please sign in again.",
  and `SessionManager.onUnauthorized()` clears the session.

Modelled as distinct types rather than message strings for a specific reason:
there is **no refresh operation** in the documented API, so a rejected token means
the session is genuinely dead. A caller that saw only a generic error would leave
a dead token in place and every later request would fail for reasons the member
cannot see. There is a test asserting offline and unauthorized are *not*
interchangeable — being offline must never sign anyone out.

## Test results

**Android — 129 unit tests + 14 instrumented, 0 failures.**
**iOS — 129 tests, 0 failures.**

Device verification:

| Case | Result |
|---|---|
| Rotate on Login | held (portrait locked) |
| Dark/light switch on Login | held (was: reset to Welcome) |
| Welcome at 2× font | body copy reachable by scroll (was: clipped) |
| Login at 2× font | fits, scrolls |
| Live call + 409 retry at 2× | controls reachable |
| iOS at accessibility-XXXL | scrolls, both buttons reachable |

## Problems hit

**I left `font_scale 2.0` set on the emulator** and the next instrumented run
failed two render tests that had nothing to do with the change. Diagnosed as my
own environment leftover, not a regression — but a reminder that device state is
part of the test fixture.

**`connectedAndroidTest` uninstalls the app afterwards**, which made a later
deep-link check appear to fail until I reinstalled.

**`simctl ui … content_size`** takes an underscore, and silently prints usage
rather than erroring when you get it wrong — so the first "largest text" check was
measuring nothing.

## Open issues / next steps

1. **iOS has no dynamic-type test gate**, only the Android one. Asserting SwiftUI
   layout needs ViewInspector or an XCUITest target; the iOS check was visual.
   Worth closing that asymmetry.
2. Remaining Phase 4 items not started: **screen-reader pass**, airplane-mode
   behaviour end to end, and performance.
3. Everything in `open-concerns.md` still stands, unchanged.
