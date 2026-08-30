# 2026-08-30 — Parity audit + first fix: nudge settings link & doc-rot sweep

## Context — a full CodePen parity audit

Ran a 6-way parallel audit of the native app against
`notes/design-reference-codepen.md` (~35 native screens). Headline: the app is in
good shape — most screens are aligned or diverge only where the code honestly and
deliberately departs from the mock (documented backend gaps, palette rules).

Real, actionable gaps found (for the backlog):
- **Notifications:** gentle-nudge "Notification settings" link opened the wrong
  screen (fixed here). Bell badge counts the read-only feed, not actionable
  nudges (Med).
- **Home grace state (35):** grace status line omits the date, hero copy doesn't
  change, grace block is additive not replacing the readiness card, Pay-now gold
  not green (Med).
- **In-call docs (30A):** missing the name·timer header + "access ends" line, and
  a flat upload list instead of the four fixed categories with View/dashed-empty
  (Med).
- **Profile hub (33):** missing "PIN & security" and "Support & intro video"
  rows (Med).
- **Customize tiles (27B):** no hold/long-press entry point on filled tiles (Med).
- **Guest gate (G3):** wrong copy + missing "Start 7-Day Limited Trial" path;
  **G1 guest-entry** absent by design (non-enumerating OTP gateway — product
  decision). **Screen 15** first-launch nudge card not built (the tour fires
  independently) — likely a deliberate consolidation, undocumented.
- Backend-blocked: Activity "Test Call/Practice run" descriptor, family join
  date, doc-section Camera/Gallery capture.

## This change — the first, cheapest fix

Picked the pure-correctness items: one real routing bug + a doc-rot sweep.

### 1. Nudge "Notification settings" link routed to the wrong screen (bug)

The gentle-nudge bottom sheet's "Notification settings" link opened the
notification **centre** (screen 24, the list of what arrived) instead of the
**settings** screen (26, the dial that tunes what arrives). One-line fix on each
platform:
- Kotlin `MainActivity.kt`: `Destination.Notifications` → `Destination.NotificationSettings`.
- Swift `AttorneyShieldApp.swift`: `destination = .notifications` → `.notificationSettings`.

(The Account settings row already routed to the settings screen correctly; only
the nudge link was wrong.)

### 2. Doc-rot sweep — comments that no longer matched shipped code

Several KDocs claimed features were "not built" that have since shipped. Corrected
on both platforms:
- **Setup (08/09):** "three steps / phone screens not built" → all five steps are
  built; the run collapses to three when the number is already verified. (Swift's
  `SetupScreen` comment was already accurate; its `SetupViewModel` comment
  self-contradicted — cleaned up.)
- **Profile completion:** "Upload documents / Common situations rows are absent"
  → both are live rows routing to the upload step and the situation picker.
- **Glovebox tile:** "no delete — `deleteUserDocument` returns forbidden" → the
  per-tile `✕` delete is live (backend fixed).
- **Account 33D:** "Screen 33D is not here / inline expiry+ZIP edit not built /
  card shown read-only" → 33D's inline expiry & billing-ZIP edit + Save (via
  `updatePaymentMethod`) is built on both platforms.

**Verified before editing, not assumed:** the audit covered Kotlin; I read the
actual Swift payment pane and Glovebox tile to confirm the same features are built
there before touching their comments. They are. I intentionally **left**
`addCardPane`'s "not built yet — contact support" copy untouched on both
platforms: *replacing* a card is genuinely still Stripe-blocked (Stage 2), so
that comment is accurate.

## Files

- kotlin: `MainActivity.kt`, `feature/setup/SetupScreen.kt`,
  `feature/profile/ProfileCompletionScreen.kt` + `ProfileCompletionViewModel.kt`,
  `feature/glovebox/GloveboxScreen.kt`, `feature/account/AccountScreen.kt` +
  `AccountViewModel.kt`.
- swift: `AttorneyShieldApp.swift`, `Feature/Setup/SetupViewModel.swift`,
  `Feature/Profile/ProfileCompletionScreen.swift` + `ProfileCompletionViewModel.swift`,
  `Feature/Glovebox/GloveboxScreen.swift`, `Feature/Account/AccountScreen.swift` +
  `AccountViewModel.swift`.

## Test results

- **Android:** `:app:compileDebugKotlin` + `:app:testDebugUnitTest` — BUILD
  SUCCESSFUL, all unit tests pass.
- **iOS:** `xcodebuild build test` (AccountViewModelTests) — BUILD SUCCEEDED,
  TEST SUCCEEDED.

The routing fix is Compose/SwiftUI navigation wiring (no VM logic), so it's
covered by compilation rather than a new unit test.
