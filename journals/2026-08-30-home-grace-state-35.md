# 2026-08-30 — Home grace state (screen 35) to CodePen parity

## Task

From the parity audit backlog: bring Home's **grace-period state (screen 35)** to
the CodePen. The audit found four divergences, all UI-side:

1. Grace status line omitted the date (a static "Grace period · renew to stay
   covered" pill instead of the spec's dated "…fully covered until <timestamp>").
2. The hero copy didn't change in grace.
3. The grace Pay-now block was *additive* (rendered below the hero) instead of
   *replacing* the readiness card.
4. Pay-now was gold, not the spec's green.

Spec (design ref §35): "the status bar is a single line in the same format as
Active and Expired, never a day count. The payment action lives at the bottom as
a green Pay now with one plain lead-in sentence … hero copy confirms access
continues but is at risk without payment."

## What shipped (both platforms)

- **Dated status line.** New `graceStatusLabel` → "Grace period · fully covered
  until Aug 13, 2026 at 9:14 PM", built from `entitlement.graceUntil` via a new
  `formatMomentAt` formatter (a "… at …" variant of `formatDateTime`, so it reads
  inside the sentence). Falls back to the plain "renew to stay covered" wording
  when a `past_due` membership carries no `graceUntil`. Uses "·" to match the
  Active/Guest pills ("same format as Active"), and an absolute timestamp, never a
  day count.
- **Hero copy in grace.** The shield hero's subtitle becomes "Tap for live legal
  help · your access continues through your grace period" (was "…— any time").
  `ShieldHero` gained a `subtitle` param; the accessibility label follows it.
- **Replaces the readiness card.** `showsReadiness` now excludes grace, and the
  settle prompt moved from under the hero to the **bottom** (after the tiles, per
  the spec's screen-text order), taking the readiness card's place. It's now a
  plain lead-in sentence + button, not a tinted card.
- **Green Pay now.** New `SuccessButton` design-system component: Verified Green
  fill (`successFill` #1E7A48) with **white** text — a fill with white on it
  (colour-system R4, 5.34:1), never green text on navy. Replaces the gold
  `PrimaryButton` for this one action.

## Decisions

- **Green button = green fill + white text**, not navy. The palette (Rank 1, R4)
  documents white-on-Verified-Green at 5.34:1 (AA); green is a fill, never text.
  Added `SuccessButton` rather than inlining Material/SwiftUI button plumbing, so
  the R4 rationale lives in the design layer and can be reused.
- **Separator "·" not the CodePen's literal "-"** in the grace pill, to match the
  sibling Active/Guest pills' format (the spec itself says "same format as
  Active"). Date is the app's house style ("MMM d, yyyy"), not the mock's
  "7/24/26" numeric form, for consistency with billing/receipts.
- **member-client (Rank 3) confirms behaviour**: grace is non-blocking (the member
  still connects via the hero), Pay Now routes to Account (`onManagePlan`). Its
  own pill lacks the date — that's the older wording; the CodePen V6 governs
  look/copy, so we show the date.
- **Deliberately skipped: the "scaled-up attorney button."** The spec enlarges the
  shield hero in grace. The shield is a finely tuned breathing animation (aura +
  two counter-breathing rings at exact sizes); scaling it risks visual bugs for a
  subtle effect, and the four items above carry the state's meaning. Noted as a
  low-value follow-up, not shipped.

## Files

- kotlin: `feature/home/HomeViewModel.kt` (graceStatusLabel, showsReadiness
  excludes grace), `feature/home/HomeScreen.kt` (dated pill, hero subtitle, grace
  block moved to bottom + `GracePayNowBlock`), `core/design/AsiComponents.kt`
  (`SuccessButton`), `core/format/Formats.kt` (`formatMomentAt`),
  `HomeViewModelTest.kt` (grace test).
- swift: `Feature/Home/HomeViewModel.swift` (graceStatusLabel on `AccountGate`,
  showsReadiness excludes grace), `Feature/Home/HomeScreen.swift`,
  `Core/Design/AsiComponents.swift` (`SuccessButton`), `Core/Format/Formats.swift`
  (`formatMomentAt`), `AccountGateTests.swift` + `HomeViewModelTests.swift`.

## Test results

- **Android**: `:app:compileDebugKotlin` + `HomeViewModelTest` — BUILD
  SUCCESSFUL. New test asserts the dated line + that grace suppresses the
  readiness card + the past_due-no-date fallback.
- **iOS**: `xcodebuild build test` (HomeViewModelTests + AccountGateTests) — BUILD
  + TEST SUCCEEDED. `graceStatusLabel` moved to the pure `AccountGate` so it's
  unit-tested directly; an async HomeViewModel test drives a grace load and
  asserts `!showsReadiness`.

## Open

- Live screenshot still pending (emulator session expired; not scanning for
  credentials). The grace state needs a `past_due`/graceUntil member to render.
- Remaining audit backlog (Tier 1): Profile hub rows (33), in-call docs (30A),
  customize-tiles hold gesture (27B), guest gate (G3).
