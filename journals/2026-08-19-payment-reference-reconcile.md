# 2026-08-19 — Reconciling the payment path against the pulled reference

## Task

`member-client` `dev` was pulled forward again (`b66e62a → 9e28d58`, 40 commits).
Before building anything new, diff the reference's payment/receipts work — and
the adversarial-audit fixes that landed with it — against what the native apps
actually do, and fix whatever genuinely applies. Repos: `member-client`
(reference), `kotlin`, `swift`, `asi-claude`.

## What the reference changed here

- **`PaymentAndPlanScreen` (new)** + `lib/paymentAndPlan.ts` — "money onto one
  screen": plan, paid amount as the heading, member composition, renewal, then
  Payment info / Sub accounts / Plan details / View invoices / Delete.
- **`SavedCardsScreen` stayed the multi-card manager** (list + make-default +
  remove), with the button reworded to **"Replace Card"** when a card already
  exists, "Add payment method" when none.
- **Two audit-fix PRs** (`88959ad`, `9154609`) — "money-path and false-promise".

## Findings against our apps

| Reference finding (audit `9154609`) | Our apps |
|---|---|
| `myMembership` showed the **base price only** — a family plan disclosed without its seat line | **Already correct.** `Membership.totalCents = lines.sumOf { totalCents }` sums every item incl. seats. |
| **`intervalCount` not selected** — a semiannual plan labelled "/mo · billed monthly" | **Already correct.** We select `intervalCount`; `formatRate` yields "/mo", "/yr", or "every N months". |
| A **family sub-account was shown the owner's** plan, price, renewal, card and **Delete account** as if their own | **Bug — we had it.** Fixed below. |

The first two are the payment discipline (money is summed, exact, interval-aware)
already holding. The third was a real defect.

### The sub-account defect (fixed)

`myMembership` deliberately falls back to the **owner's** membership for a
sub-account so they can see their coverage. Our `PlanPane` / `planPane` (screen
33A) rendered that fallback verbatim — the owner's plan card, rate, payment-method
row, billing history and the red **Delete account** — to someone who owns none of
it. The reference guards its four sibling money screens on `ent.isSubaccount`;
this one had been missed on both sides.

Fix (both platforms): when `isSubaccount`, 33A shows only a **"Covered by a family
membership"** card ("Your coverage comes from {plan}. Contact the membership owner
for billing, invoices or plan changes.") and nothing else — no rate, no card, no
Delete. The primary owner's view is unchanged (`isSubaccount == false`).

## On our 33D divergence

The reference's payment-methods screen is still the **manager**, not the CodePen
33D single-card screen we now ship. That divergence is the user's explicit,
recorded choice (CodePen look over `member-client` behaviour) — left as is. The
reference's new **"Replace Card"** wording actually lines up with our "Replace
with a new card", so the two are closer than they look. See
[[2026-08-19-payment-methods-stripe]].

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — `AccountViewModelTests` | **5 / 5 passed** |

Not visually confirmed on-device: the sub-account state needs a sub-account login
(the test account `munyira851@…` is a primary owner, `isSubaccount == false`).

## Open / next

1. **Profile hub row** — the Account hub's "Payment & plan" row shows the rate
   (`$X/mo`) as its subtitle; for a sub-account that is still the owner's money.
   Same principle as the 33A fix — worth guarding, not yet done.
2. **Broader `dev` drift** — registration / account-setup / checkout / nudges /
   call additions are pulled but unreconciled; a separate planned pass.
3. **Stage 2 Stripe** — still blocked on dev Stripe config + the iOS SPM tooling
   risk. See [[2026-08-19-payment-methods-stripe]].