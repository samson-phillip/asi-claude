# 2026-08-11 — Phase 2 (slice 1): welcome carousel and login

## Task
Build the Stage 1 welcome carousel and the login UI on both platforms, set the
real app IDs, and start a running register of backend gaps plus a message to
send the backend team.

## Repos and files touched

**`kotlin`** — `feature/welcome/{WelcomeContent,WelcomeHeroes,WelcomeScreen}.kt`,
`feature/auth/{LoginViewModel,LoginScreen}.kt`, `MainActivity.kt` (routing),
`core/design/AsiComponents.kt` (+`ShieldLockup`, `AsiTextField`,
`AsiErrorBanner`), `core/network/AsiApi.kt` (injectable IO dispatcher),
`app/build.gradle.kts` (applicationId, debug suffix), tests
`LoginViewModelTest.kt`, `WelcomeContentTest.kt`.

**`swift`** — `Feature/Welcome/{WelcomeContent,WelcomeHeroes,WelcomeScreen}.swift`,
`Feature/Auth/{LoginViewModel,LoginScreen}.swift`, `AttorneyShieldApp.swift`
(routing), `Core/Design/AsiComponents.swift` (same three components),
`Core/Session/SessionStore.swift` (Keychain service follows the bundle id),
`project.pbxproj` (bundle ids), tests `WelcomeContentTests.swift`,
`LoginViewModelTests.swift`.

**`asi-claude`** — `notes/backend-gaps.md`, `notes/backend-message-draft.md`,
this journal.

## App IDs

Both set to `com.app.attorney.shield` as given.

Android keeps `namespace = com.attorneyshield.member` — it drives the
`R`/`BuildConfig` package and matches the source tree, and it is independent of
the store identity. Renaming ~30 files' packages would be churn for no benefit.

## The carousel

Six swipeable pages. The reference's frame 0 is a static splash, which belongs
to app launch rather than the carousel, so it is not a page.

Copy is transcribed verbatim and pinned by test — the CodePen banner calls
screens 1–6 "the locked reference for the app welcome flow", so the wording is
not ours to improvise. `WelcomeContentTest`/`WelcomeContentTests` assert the six
headlines and eyebrows exactly, that the "law enforcement-initiated" scoping
survives on the four pages that use it (it is legally load-bearing — the product
is scoped to police encounters, not general legal advice), and that screen 5
keeps its "illustrative benefit example / not an in-app claim" disclaimer.

Five of the six heroes are UI compositions in the reference and port directly.
Screen 1's is photographic, so it is rebuilt as the same *structure* — call
surface, LIVE ATTORNEY / SECURE pills, self-view tile, attorney caption — with a
placeholder where the photo goes, so the layout is right when real art lands.

Screen 4's tool caption rotates on the reference's 3800ms cadence and is gated
on reduce-motion, matching the reference's own `prefers-reduced-motion` gate.

The active page dot **widens** rather than only changing colour, so position is
readable without colour perception.

## Login

Email + password, which is what the gateway's `login` mutation supports.

**The reference's own sign-in is not this.** Screen 13A says members can "sign in
with a one-time text code instead" of a password, and the only sign-in screen the
CodePen draws is G1's *error* state ("We couldn't find that email"). There is no
OTP endpoint in the documented API, so email + password is the buildable subset.
Logged as backend gap §3.

Deliberate call: **no client-side email regex.** The server is the authority on
whether an address exists, and a pattern that rejects a valid address locks
someone out of their own account for no benefit. There is a test naming this so
it does not get "fixed" later.

Errors show whatever the gateway said — "invalid credentials" beats a shrug —
and are rendered in the gold accent, never an unapproved red (§9.4 still open).

## Problems hit

**`com.app.attorney.shield` is already installed and live.** The emulator had it
at **versionCode 126** (internally `com.example.attorneyshield`), so our v1 build
was rejected as a downgrade. Rather than uninstall someone's app, debug builds
now carry `applicationIdSuffix = ".debug"` so 2.0 installs alongside the shipped
app instead of clobbering it. **Consequence for release: the first 2.0 build must
have `versionCode` above 126.**

**A clipped tile.** The incident-tile hero has five tiles over three rows and did
not fit the shared 232dp hero height — the last row compressed until "Pedestrian"
vanished. Hero height is now a parameter (258 for that one). Caught by looking at
the screenshot, not by a test; worth remembering that layout overflow is silent.

**`advanceUntilIdle()` could not drive the login tests.** The HTTP call sat on
`Dispatchers.IO`, which the test scheduler cannot advance, so every assertion saw
an untouched state and zero requests. Fixed properly by making the IO dispatcher
injectable on `AsiApi` rather than by sleeping in tests. Also needed
`runTest(dispatcher)` so `viewModelScope` and `advanceUntilIdle` share one
scheduler.

## Test results

**Android — 79 unit tests, 0 failures.**

| Suite | Tests |
|---|---|
| `AsiApiTest` | 28 |
| `AsiContrastTest` | 17 |
| `SessionManagerTest` | 12 |
| `LoginViewModelTest` | 10 |
| `WelcomeContentTest` | 8 |
| `PaletteAllowlistTest` | 4 |

**iOS — 84 tests, 0 failures.**

**Device verification.** Both platforms installed and driven by hand: carousel
swiped through, all five incident tiles confirmed present after the fix, and the
login screen reached from the Log in button with its disabled Sign-in state
correct. Android checked in both appearances.

## API endpoints used
None live — the gateway URL is still unknown (backend gap §1). All tests run
against MockWebServer / a `URLProtocol` stub.

## Open issues / next steps

1. **Send `notes/backend-message-draft.md`.** The gateway URL and a dev login
   are what unblock a real end-to-end sign-in.
2. Home, Call, and the deep-link handler are the rest of Phase 2.
3. Release `versionCode` must exceed 126 (see above).
4. No launcher icon or brand shield asset yet — the lockup draws a placeholder
   shield in gold so nothing is missing on screen.
5. Screen 1's hero needs the real attorney photography.
6. `Register` opens `https://attorney-shield.com` as a placeholder; the true
   plan-page path is backend gap §6.
