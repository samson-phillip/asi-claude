# 2026-08-11 — Phase 2 (slice 3): the deep-link handler

## Task
Handle the web→app handoff after checkout (reference screens 07 and T4), on both
platforms. Completes Phase 2's spine.

## Repos and files touched

**`kotlin`** — `core/deeplink/DeepLink.kt`, `AndroidManifest.xml` (App Links
intent-filter, `singleTask`), `MainActivity.kt` (cold + warm handling),
`DeepLinkParserTest.kt`, plus a race fix in `HomeViewModelTest.kt`.

**`swift`** — `Core/DeepLink/DeepLink.swift`, `Config/Info.plist` (private
scheme), `project.pbxproj`, `AttorneyShieldApp.swift` (`onOpenURL`),
`DeepLinkParserTests.swift`, plus a race fix in `StubURLProtocol.swift` and
`HomeViewModelTests.swift`.

**`asi-claude`** — this journal.

## The contract is provisional, and confined

The reference never records the actual path or parameter names — it only says a
deep link hands the member back "with email pre-filled". So the parser accepts
the plausible spellings (`/app/return`, `/return-to-app`, `/app`) and everything
lives in one file, so a confirmed contract is a one-line change. Logged as
backend gap §6.

## Treated as attacker-controlled input

A deep link is something anyone can send — from a text message, a web page, or
another app. So the parser refuses more than it accepts:

- **https only.** A plaintext link can be rewritten in transit, so `http` is
  refused even on the right host.
- **Exact host allow-list.** `evil.attorney-shield.com` and
  `attorney-shield.com.attacker.example` are both refused; a subdomain is not
  implied by the parent.
- **The email is a text-field prefill, nothing more.** A link cannot sign anyone
  in, so a forged one costs an attacker a typed address. There is a test
  asserting that a link carrying `accessToken`, `userID` and `roles` yields
  *only* the email.
- Anything unrecognised returns null rather than being guessed at.

## Where the link lands

The reference resumes native registration at screen 08. Those screens have no
endpoints, so the honest landing is **sign-in with the email pre-filled** — by
this point the member has an account, they just need to get into it. One line to
redirect once 08 exists.

## Decisions and why

**`java.net.URI`, not `android.net.Uri`.** The platform class is a stub on the
JVM unit-test classpath — the same trap as `org.json` earlier this week — so
using it would have pushed all 17 parser cases onto a device for no reason.

**A private scheme (`attorneyshield://return`) alongside the https links.**
Universal Links need an Associated Domains entitlement and an
`apple-app-site-association` file on both hosts; Android App Links need
`assetlinks.json`. **Neither exists**, so without a fallback the iOS handler
could not be exercised at all. It also backs the reference's own "Open app
manually" affordance on screens 07/T4. Documented as weaker than a Universal
Link — any app can claim a private scheme — which is only tolerable because the
link carries no authority.

## Test results

**Android — 124 unit tests, 0 failures** (17 new for the parser).
**iOS — 124 tests, 0 failures** (18 new).

**Device verification, Android** — driven with `am start`, reading the UI with
`uiautomator dump`:

| Case | Result |
|---|---|
| T-D-2 cold start from the link | Login, `member@example.com` pre-filled |
| T-D-1 warm handoff | Login, `warm@example.com` pre-filled |
| T-D-8 foreign host, force-delivered to our package | **stayed on Welcome** |

Sign in stayed disabled throughout, since the link supplies no password — which
is the point.

**Device verification, iOS** — `simctl openurl` with the private scheme: the OS
confirmed "Open in AttorneyShield?", and accepting landed on Sign in with
`member@example.com` pre-filled.

## Problems hit

**A latent test race, on both platforms.** `HomeViewModel` issues its two queries
*concurrently*, but both stubs answered FIFO regardless of which request arrived
— so the two in-flight requests could receive each other's responses. iOS caught
it as a failure; Android had been passing on luck. Both stubs now match on
request content (`MockWebServer.Dispatcher` on Android, a `match:` substring on
the iOS handle). Worth remembering: FIFO stubbing is only safe for sequential
requests.

**XML comments cannot contain `--`.** The manifest comment used it as a dash and
the merger failed with only "Error parsing AndroidManifest.xml".

**`Info.plist` cannot live inside a synchronized folder group.** Xcode both
copies it as a resource and consumes it as the target plist — "Multiple commands
produce Info.plist". Moved to `Config/`.

## API endpoints used
None.

## Open issues / next steps

1. **`assetlinks.json` and `apple-app-site-association` are needed on both hosts**
   for the links to open the app *silently*. Until then Android shows a
   disambiguation dialog and iOS Universal Links do not fire at all. This is a
   web/backend task — added to the backend gaps.
2. **Confirm the real deep-link URL** (backend gap §6) — the accepted paths are a
   guess.
3. Phase 2's remaining work is attaching the Vonage publisher/subscriber views to
   the live call state, and wiring mute through to the publisher. Both want a real
   call to be worth testing.
4. Still owed: a visual pass over Home and Call once a login works.

---

## Addendum — Vonage video attached to the Call screen

Completes Phase 2. `VonageSession` now hands out the publisher and subscriber
surfaces as plain platform views (`android.view.View` / `UIView`) rather than SDK
types, so the UI layer never imports the SDK — the video surface is the only part
of a call that has to be an SDK object, and confining it keeps the rest
swappable.

**Mute now reaches the publisher**, not just the button. A mute control that
leaves the microphone transmitting would be a serious defect on a call whose
whole purpose is a legal encounter, and it was UI-only until now.

**Teardown is the guarantee that matters**, so the session lives in a
`DisposableEffect` (Android) / `onDisappear` + `onChange` (iOS): leaving the
screen releases the camera, mic and socket even if the member backed out
mid-connect.

Both platforms re-parent the SDK view rather than rebuilding it. A naive
teardown-and-recreate on every update would rebuild the video surface on
unrelated state changes — visible as a flicker mid-call.

**Unverified, and worth being explicit:** a real video call has never connected,
because `member-call` returns 409 with no attorney on dev. What *is* proven is
that the SDK loads, reaches Vonage, and reports through the phase machine (the
Phase 0 spike), and that the credential and lifecycle plumbing compiles and
tears down cleanly. The step from "connecting" to a live picture is the one thing
still taken on faith.

Android 124 unit + 9 instrumented, iOS 124 — all green after the change.
