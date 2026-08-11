# 2026-08-11 — Phase 2 (slice 2): Home and Call

## Task
Build the Home screen and the full call flow on both platforms.

## Repos and files touched

**`kotlin`** — `feature/home/{HomeViewModel,HomeScreen,ConnectSheets}.kt`,
`feature/call/{CallViewModel,CallScreen}.kt`,
`core/location/MemberLocation.kt`, `MainActivity.kt` (routing + permissions),
`AndroidManifest.xml` (camera/mic/location), tests
`HomeViewModelTest.kt`, `CallViewModelTest.kt`,
`androidTest/feature/ScreenRenderTest.kt`.

**`swift`** — `Feature/Home/{HomeViewModel,HomeScreen,ConnectSheets}.swift`,
`Feature/Call/{CallViewModel,CallScreen}.swift`,
`Core/Location/MemberLocationProvider.swift`, `AttorneyShieldApp.swift`
(routing), `project.pbxproj` (camera/mic/location usage strings), tests
`HomeViewModelTests.swift`, `CallViewModelTests.swift`.

**`asi-claude`** — this journal.

## Both connect paths, as the reference specifies

The reference is precise about this and it would be easy to get wrong:

- **Shield hero → incident tray (27A):** a tap on a tray tile **connects
  directly**. "Tapping an incident is the action itself... No selection state, no
  checkmark, no extra confirmation."
- **Home tile → confirmation sheet (28):** "The confirmation exists only on this
  path, to prevent accidental connections from the home screen."

So the same incident reached two ways behaves differently, on purpose. Both land
in one `begin()` path so the routing and call setup cannot drift between them.

## What Home deliberately does not have

The reference's saved "three most common situations", the readiness card, and the
Glovebox/Activity/Profile tab bar. None have endpoints
(`notes/backend-gaps.md` §5), and shipping navigation to nowhere is worse than
leaving it out — so Home carries the full incident list until a preferences API
exists. This is a scope decision, not an oversight.

## Call flow

Sequence ported from `member-client`: best-effort location → `member-call` →
credentials to the Vonage session → follow its callbacks through `CallPhase`.

Behaviours held by test:

- **409 → `noAttorney`, retryable**, with the reference's own wording. Not an
  error state, and it has a Try again button that a generic error does not.
- **Location never blocks the call.** Null is fine; so is *throwing*. The Android
  test deliberately supplies a provider that raises, and the call still goes out.
- **Credentials are validated before the SDK is touched**, so a blank token never
  becomes an opaque Vonage failure later.
- The live timer only advances in `live`, and formats past a minute.
- Hang-up is an **outlined** control, not red — the palette forbids the red it
  names and supplies no error colour (development plan §9.4 still open).

Connecting shows the reference's three rotating tips verbatim on its 4s cadence,
gated on reduce-motion, with the encryption line fixed above Cancel.

## Decisions and why

**Location uses the platform APIs, not Play Services.** `LocationManager` on
Android, `CLLocationManager` on iOS. One of the emulators on this machine is
deGoogled, and more to the point an optional field is not worth a hard Google
dependency. Both check a cached fix first — a recent one beats making someone
wait mid-encounter — then fall back to a single timed request.

**Camera and mic are requested at point of use; location is not requested
alongside them.** Asking for three permissions at once invites a blanket denial,
and location is the one we can do without.

**Verification method for these two screens was assertion, not eyeballing.**
Reaching Home through the app needs a live login, and the gateway URL is still
unknown (§1). A debug-only auth bypass would have been worse than testing the
screens directly, so Android renders Home and every Call phase in instrumented
tests that assert on-device content. **I have not visually inspected Home or
Call on device** — worth saying plainly, because the clipped-tile bug earlier
this session was invisible to text assertions. Both screens scroll rather than
sitting in fixed-height containers, so that specific failure mode cannot recur,
but a visual pass is still owed once a login works.

## Test results

**Android — 107 unit tests + 9 instrumented, 0 failures.**

| Suite | Tests |
|---|---|
| `AsiApiTest` | 28 |
| `AsiContrastTest` | 17 |
| `CallViewModelTest` | 17 |
| `SessionManagerTest` | 12 |
| `HomeViewModelTest` | 11 |
| `LoginViewModelTest` | 10 |
| `WelcomeContentTest` | 8 |
| `PaletteAllowlistTest` | 4 |
| `ScreenRenderTest` (device) | 6 |
| `VonageSdkSpikeTest` (device) | 3 |

**iOS — 107 tests, 0 failures**, with `CallViewModelTests` 15 and
`HomeViewModelTests` 8 mirroring the Android suites.

## Problems hit

**A flaky spike test, found by running it again.** `VonageSdkSpikeTest` mutated
plain `MutableList`s from the SDK's callback thread while the assertions read
them, and threw `ConcurrentModificationException` under load. It had passed
twice before. Now `CopyOnWriteArrayList`. Worth remembering that a test which
touches a callback thread is concurrent whether or not it looks it.

**Kotlin's `body` collision on iOS.** `TerminalState` had a `let body: String`
alongside SwiftUI's `body` requirement; renamed to `message`.

## API endpoints used
None live. All tests run against MockWebServer / a `URLProtocol` stub. The one
real call this session was the earlier `member-call` 409.

## Open issues / next steps

1. **Send `notes/backend-message-draft.md`** — the gateway URL and a dev login
   unblock a real sign-in and a visual pass over Home and Call.
2. **The Vonage session is not attached to the Call screen's UI yet.** The phase
   machine, credentials and chrome are all in place; wiring the publisher and
   subscriber views into the live state is the next piece, and needs a real call
   to be worth testing.
3. **Deep-link handler** is the remaining Phase 2 item.
4. `iconFilePath` is ignored — no image loader is wired, so the code's emoji
   stands in for uploaded incident icons.
5. Mute is UI-only so far; it needs to reach the Vonage publisher.
