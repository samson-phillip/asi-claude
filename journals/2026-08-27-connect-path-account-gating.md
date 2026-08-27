# 2026-08-27 — Wire the connect-path account gates (guest / grace / expired)

## Task

Finish the connect-path gating begun with the trial fix. "Wire the rest": a
**guest** upsell, **grace** handling, and **expired/canceled** handling on the
connect path, mirroring the updated `member-client` (which gates all four states
client-side). Also: use member-client's gating to answer the three backend
questions filed in `notes/account-states-trial-grace-guest-profile.md` §5.

Repos: `kotlin`, `swift`. Reference: `member-client` `src/screens/HomeScreen.tsx`,
`src/state/guest.tsx`, `src/state/trial.tsx`, `src/lib/trialGate.ts` (read-only).

## Model (from member-client, palette + CodePen for look)

Gate the live call on **entitlement + segmentation, never the membership status
string** — exactly member-client's rule.

- `canCall = entitlement.entitled || membership.statusCode ∈ {active, trial}`
  (ORed for resilience — one failed read never gates a covered member).
- `isGuest = segmentation ∈ {guest_user, member_lead} && !canCall`.
- `inGrace = canCall && (entitlement.graceUntil set || status == past_due)` — **non-blocking**.
- `paymentFailed = !canCall && status == past_due`.
- `isExpiredMember = !canCall && !guest && !trial && !paymentFailed && (have some account data)`.
- Tap order (member-client `start()`): **guest upsell → trial V2 gate → renew wall → connect**.

Two deliberate safety choices, both documented in code:

1. **Fail OPEN, evidence-based.** The expired wall only fires with *positive*
   evidence of a lapse (an entitlement or membership row came back). Two failed
   reads show the tiles rather than hiding them — a stray tap is now caught by the
   45s ring timeout (the NoAnswer phase), so fail-open is safe. This diverges from
   member-client (which fails to "choose a plan") in favour of the app's own "one
   tap from an attorney" principle, since I can't reproduce every state on device.
2. **Everything waits on `accountLoaded`** so no pill/card flashes mid-load.

### CTAs, given the checkout funnel is API-blocked (dev-plan §3)

No native plans/checkout screen exists. So:
- Guest "View pricing plans" and the expired "View plans" **hand off to the web
  checkout** (the Welcome screen's existing `planUrl`) — a working action, not
  dead nav.
- Grace "Pay now" and payment-failed "Update payment" → **Account** (where the
  card on file lives). Grace is non-blocking; the member still connects.

## Changes

**kotlin**
- `feature/home/HomeViewModel.kt` — fetch `getEntitlement` alongside membership;
  added `entitlement`, `accountLoaded`, and derived `canCall/isGuest/inGrace/
  paymentFailed/isExpiredMember/connectBlocked/showsTiles` on `HomeUiState`.
- `feature/home/HomeScreen.kt` — state-driven `CoveragePill` (Active/Grace/Guest
  tones), `GraceCard`/`RenewCard`/`PaymentFailedCard` (shared `HomeNoticeCard`),
  locked-tile treatment, heading suppressed when tiles are replaced,
  `onManagePlan`/`onViewPlans` callbacks.
- `feature/home/ConnectSheets.kt` — new `GuestUpsellSheet` (FloatingSheet).
- `MainActivity.kt` — shared `gatedConnect` on both entry points; guest sheet
  mounted; `onManagePlan → Account`, `onViewPlans → openWebRegistration`.
- `feature/home/HomeViewModelTest.kt` — 9 new pure-state tests.

**swift** (line-for-line mirror)
- `Feature/Home/HomeViewModel.swift` — new pure `AccountGate` struct holding the
  same logic (member-client's `trialGate.ts`-style split, so it is testable
  without a VM); VM fetches entitlement in `loadAccount()`, forwards the flags.
- `Feature/Home/HomeScreen.swift` — pill tones, notice cards, locked tiles, gated
  Group, `onManagePlan`/`onViewPlans`.
- `Feature/Home/ConnectSheets.swift` — `GuestUpsellSheet`.
- `AttorneyShieldApp.swift` — `gatedConnect`, guest sheet mount, CTA wiring.
- `AttorneyShieldTests/AccountGateTests.swift` — 11 new tests.
- `AttorneyShieldTests/VonageSdkSpikeTests.swift` — fixed a **stale** terminal-phase
  test (`noAnswer` had joined the terminal set in the earlier decline work but this
  Swift test still asserted three; the Kotlin twin was already updated).

## Backend questions — closed by member-client

All three (`profile` §5) are answerable from the reference and need **no** backend
change to ship: Q1 trial signal = `myMembership.status.code == "trial"` with a
fail-closed `unknown`; Q2 the client fails safe by construction (never offers the
call when `!canCall`); Q3 `entitled` is the "covered" truth, `entitled && !trial`
the "connect live" truth. Full write-up in `profile` §5a. The separate real-time
**decline/no-pickup** ask still stands (ring timeout is the interim).

## API endpoints used

`membershipEntitlement(organizationID)` (new read on Home), `myMembership`
(already read), `myAccountStatus` (already on the session). No new endpoints.

## Test results

| Suite | Result |
|---|---|
| Android `testDebugUnitTest` (full) | **BUILD SUCCESSFUL** — incl. 9 new Home cases |
| iOS `xcodebuild test` (AttorneyShieldTests) | **TEST SUCCEEDED** — 442 tests, incl. 11 new `AccountGateTests` + fixed CallPhase test |
| Android emulator (Pixel_8a_API_35) | Installs, launches, Home renders the new gating path (**Guest explorer** pill, no crash, layout intact) |

## Open issues / next steps

- **Clean device pass pending.** The emulator's persisted session was stale
  (backend returning "unauthorized"), and the signed-in test account is segmented
  guest/lead — so I saw the guest path, not a clean member/grace/expired sweep.
  Needs a fresh login as a member (and, ideally, seeded grace/expired accounts) to
  verify Active-pill + tiles, the grace card, and the renew wall end-to-end.
- **Optional hardening:** adopt member-client's fail-closed-on-`unknown` for the
  trial gate (we currently OR two positive signals).
- The trial gate still needs a `Membership` to open; a segmentation-only fresh
  trial with a null membership row falls through (pre-existing, out of scope).
