# 2026-08-14 — Trial gate and conversion (V2, T5–T8)

## Task

Build the in-app trial flow — design branch B2. A member on the 7-day trial who
taps to connect is stopped by a gate (**V2**) instead of reaching a live
attorney; from there they can start their paid membership. Confirming shows the
charge notice (**T5** individual / **T6** family), then processing (**T7**),
then the receipt (**T8**). This is the app-side of B5, which the backend
answered with `convertMyTrial`.

## Repos and files touched

### `kotlin`
| File | What |
|---|---|
| `core/network/AccountModels.kt` | `Membership.isTrial`, `TrialConversion`, wire types. |
| `core/network/AsiApi.kt` | `convertMyTrial`; extracted a shared `toMembership` mapper. |
| `feature/trial/TrialViewModel.kt` | **New.** The gate→notice→processing→confirmed state machine. |
| `feature/trial/TrialSheets.kt` | **New.** V2/T5–T8 as one `ModalBottomSheet`. |
| `feature/home/HomeViewModel.kt` | Loads the membership; `isTrial`; `refreshMembership`. |
| `MainActivity.kt` | Gate intercepts both connect entry points. |
| `.../trial/TrialViewModelTest.kt` | **New.** 6 tests. |

### `swift`
Same shape: `TrialViewModel.swift` (`@Observable @MainActor`), `TrialFlow.swift`
(the sheet), plus the model/API/Home/App wiring and `TrialViewModelTests.swift`
(7 tests).

## The decisions that matter

### Data-driven, not the design's numbers

The mockups show "FreedomPlus $16/mo" and "FreedomFAMILY $38/mo". The screens
render **none of that literally**. Plan name, price, interval and member count
all come from the member's real `myMembership` + `membershipEntitlement`. T5 vs
T6 is chosen from the actual **seat allowance** (`includedSubaccounts`), falling
back to whether the plan name contains "family", so it survives a product
rename. This is the CLAUDE.md rule — take colour from the palette, take
everything factual from the API, never hardcode.

Confirmed necessary by the dev catalog: the real products are
Individual/Family × Annual/Semiannual at various prices, not "$16/$38" at all.

### The card is already on file

`convertMyTrial` **charges the card captured at web trial-signup (T2)** — it
does not collect one. So T5–T8 need no card entry and no Stripe SDK widget. A
failed charge (most often "no card on file") lands back on the notice **with the
reason**, never a dead end — the whole point of the sheet is honesty about the
charge. `alreadyConverted` guards a double-tap.

### `isTrial` keys on the status, not on `trialEnd`

`isTrial = statusCode == "trialing"`. Not "`trialEnd` is present": `trialEnd`
lingers as history after a trial converts, so testing it would keep gating a
member who has already paid. After a successful conversion, Home **re-reads the
membership** so the next tap connects instead of re-gating.

### The gate is the only path for a trial member

Both connect entry points on Home — the hero shield and a situation tile — open
V2 when `isTrial`, whatever the entry. A trial member never slips into the
live-connect flow.

### The "AI demo" button is honest about a gap

V2's second action, "Try the AI demo instead", **closes the gate**. There is no
guided-AI-demo endpoint or screen; routing a trial member into the live-connect
flow would defeat the gate. Commented in both apps and flagged as a product gap
rather than faked.

## Live verification (dev, Stripe TEST mode)

**Stripe is in test mode** — `stripePublishableKey` returns `pk_test_…`, so the
user's point stands: test cards move no real money. Verified against dev with
munyira851's real membership (org `6c53e00d…`, not the dev-default org — that
was why an earlier `myMembership` read came back null):

| Checked | Result |
|---|---|
| `convertMyTrial` payload shape | ✅ Returns `status` / `alreadyConverted` / `membership{status{code}}` exactly as the model parses. |
| `alreadyConverted` path | ✅ Calling it on an already-active membership returned `true` with **no** new charge. |
| Error path | ✅ On the dev-default org (no membership): "you do not have a membership to convert" — a clean message the UI surfaces. |
| `myMembership` real data | ✅ "Freedom Basic — Family" $38 + 2 seats ×$4 = $46/mo; family plan → `isFamilyPlan` true. |
| Card on file | ✅ `myPaymentMethods` → **Visa •••• 4242** (`isDefault`), the exact T5/T6/T7 line — and a test card, confirming test mode end to end. |
| `status.code` format | ✅ Lowercase Stripe-style (`"active"`) → `isTrial` correctly false. |

**The one thing not confirmed live:** the exact `"trialing"` string for a
*trial* membership. This dev org has **no Stripe-linked prices**
(`planProducts.stripePriceID` is null, `resolvePrice` returns null), so a
chargeable trial cannot be minted here — same family as S2 (dev data not set up
for the flow). `"trialing"` is the Stripe subscription-status standard and the
gateway mirrors Stripe (`status.code` is lowercase Stripe values), so the
assumption is sound; it wants one confirmation against a real trial member when
the backend can provide one. **On-device visual of the gate is likewise pending
a trial account** — no available account is `trialing`, so the gate does not
fire for them (correctly).

## Test results

**Android — 416 tests, 0 failures** (6 new). **iOS — 394 tests, 0 failures**
(7 new). Covered on both: `isTrial` true/false, individual vs family
member-line, open→gate→card load, convert→receipt, no-card error returns to the
notice, "Not now" returns to the gate.

## Open issues / next steps

- **Confirm the trial `status.code` string** against a real trial member, and do
  the on-device visual pass, once the backend seeds a Stripe-linked trial on dev
  (ask logged with S2).
- **The guided AI demo** (V2's second action) has no backend — product gap.
- The **web trial-signup screens V1, T1–T4** are a separate, web surface and
  remain out of scope for the native app.
- Still open elsewhere: S1 (member-token admin hole), S2 (queue-routable
  attorney / live two-way), the guest model (B5a).
