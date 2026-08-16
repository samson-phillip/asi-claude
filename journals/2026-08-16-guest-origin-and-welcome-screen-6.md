# 2026-08-16 — Guest sign-up wiring, and welcome screen 6

## Task

1. Send `origin: APP` on `verifyLoginOtp` and read `myAccountStatus` after
   sign-in, closing the gap found when the guest-user API was reviewed.
2. Build **welcome screen 6** to the client mockup — the pin-map of the United
   States with lights that bloom and fade.

## Part 1 — guest segmentation

### A correction to yesterday's write-up

I said "both apps already send `countryISO2`". That is wrong, and worth
recording. The *query* declares the argument, but **no call site ever populates
it** — `signInWithOtp` calls `verifyLoginOtp(email, code)` and the parameter
defaults to null. `TimeZoneCountry.current()` exists but feeds `member-call`,
not sign-in.

It is left null deliberately. `countryISO2` is stamped as the member's **home**
country, which the gateway says drives products, currency and billing. A device
region is not a home country, and stamping one from the locale is a product
decision, not ours. Recorded in backend-gaps.md §9 as a question rather than
silently changed.

### What changed

`verifyLoginOtp` now takes `origin: SignupOrigin = APP`. It is a **default, not
a call-site choice**, because every sign-in from this app is by definition from
the app — and the gateway ignores it entirely for an account that already
exists. The mutation declares `$origin: SignupOrigin` so the gateway type-checks
it.

`myAccountStatus` is a new query resolved in `adopt()` alongside `getMe` and
`getCasesByUser` — best-effort, wrapped so a failure cannot cost a member their
sign-in — and carried on `MemberContext.accountStatus`.

**Null is a real answer**, not a failure: accounts provisioned before the
backend's segmentation migration have nothing stored, and the gateway's guidance
is to treat that as *unknown* and fall back to entitlement rather than reading it
as "not a guest". Both platforms document that at the field.

`refreshContext` re-reads the status too, so a guest who buys a plan stops being
shown guest UI. On iOS that also fixed a latent bug: unlike Android's `copy()`,
iOS rebuilds `MemberContext` field by field, so the status would have been
silently dropped on every refresh.

### Tests

Three new on Android, two on iOS, and they assert **on the wire**, not on the
language default — the wire is what the gateway sees:

- `origin` is sent as `APP` and declared as `SignupOrigin`
- the status is resolved, kept, and survives being persisted
- a failing or unsegmented status leaves the sign-in intact and the field null

Adding a fourth request to `adopt()` broke five existing sign-in fixtures, which
is the tests doing their job: they enqueue responses in strict order. Fixed by
adding the status response after `casesByUser` and taking four requests instead
of three.

## Part 2 — screen 6

The reference's own behaviour (`data-random-map-lights`, CSS 5542–5615, JS
14715–14764), not a fixed set of dots:

- **26** candidate positions tracing the populated parts of the silhouette, so a
  light never blooms out in the ocean.
- **5** lights, each picking a spot no other light holds, blooming for a random
  1900–2900ms, then dark for 450–1650ms before moving somewhere new.
- Starts staggered `220 + index * 610` plus jitter, so they never pulse together.
- The bloom is a four-stop curve: in fast to 0.92, hold, swell to 1.14, fade to
  0.76 — composited `mix-blend-mode: screen`, which is what makes them read as
  light rather than as paint. Both platforms use a Screen blend for that.

The map is the reference's own 820×820 JPEG, bundled. The navy proof banner
carries the two metrics `WelcomeContent.nationwideStats` already held.

Screen 6 is the **third light stage**, so the wordmark and status bar flip to
navy and it gets its own cream-to-amber wash with a gold bloom behind the map.

### The stage bug this surfaced

Adding a third layered stage exposed a real fault in yesterday's work: the light
pages painted an **opaque flat cream over the shared backdrop**, which hid the
layered wash behind them. Screen 5 shipped yesterday with its gold/green wash
invisible on Android for exactly this reason.

The reference's `.hero-N` is one element spanning the status bar, wordmark and
art, so a single backdrop is right and the per-page paint was wrong. On Android
the backdrop is now blended from **the pager's scroll offset** rather than the
settled page: at rest it is one page's stage exactly, mid-swipe a true blend of
two, so pages can stay transparent and no cream page is ever seen over a navy
backdrop. SwiftUI's `TabView` does not expose that offset, so iOS keeps a
per-page paint but paints the page's **full layered stage** instead of a flat
colour.

### Two platform-specific faults, both found by looking

- **Android:** the banner's metrics rendered navy-on-navy. It is a dark card on
  a *light* stage, and `accentText` on light is Shield Navy — so the values are
  now explicitly Active Gold. A theme token was the wrong tool there.
- **iOS:** the lights did not render at all. I diagnosed it by elimination
  rather than guessing — a plain circle rendered, a circle with `.blendMode`
  rendered, a marker inside `if animate` rendered — which left the light's own
  view, whose `@State` was being driven from a detached async loop SwiftUI was
  not tracking. Rewrote it as a pure function of a `TimelineView` clock, so the
  bloom cannot get out of step with rendering. Each light draws from its **own
  band** of the 26 positions, which gets the "no two lights share a spot"
  invariant without any shared mutable state.

## Files

- **kotlin**: `AsiApi.kt`, `Models.kt` (`SignupOrigin`, `MemberStatusRef`),
  `MemberContext.kt`, `SessionManager.kt`, `WelcomeHeroes.kt` (screen 6),
  `WelcomeScreen.kt` (offset-blended stage, `drawNationwideStage`),
  `res/drawable-nodpi/welcome_hero_us_map.jpg`, two test files.
- **swift**: `AsiApi.swift`, `Models.swift`, `MemberContext.swift`,
  `SessionManager.swift`, `WelcomeHeroes.swift` (screen 6),
  `WelcomeScreen.swift`, `Media.xcassets/welcome_hero_us_map`, `AsiApiTests`.

No palette values added.

## Tests

| Suite | Result |
|---|---|
| Android unit | **432 / 432** (3 new), 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **413 / 413** (2 new), 0 failed |

Screen 6 verified by eye on the Pixel 8a emulator and the iPhone 16 Pro, and the
lights confirmed to *move* by frame-diffing rather than by a single screenshot —
~700 changed pixels per frame pair on Android, and visibly different positions
across two iOS frames.

## Open issues / next steps

- **All six welcome screens now match their mockups.** The carousel is done
  unless the client revises one.
- **Nobody has exercised guest sign-up end to end.** The wiring is tested
  against the wire but never against the live gateway, because signing up means
  creating an account. One real run would confirm the account comes back as
  `guest_user`.
- **The gold-eyebrow ruling is still outstanding** (screens 3, 4, 5).
- Still open: the **blue stage lift on screen 3** has no palette equivalent, and
  the **sheet body copy clips mid-glyph** on short screens.
- The reference's **per-icon keyframes on screen 4** remain unbuilt.
