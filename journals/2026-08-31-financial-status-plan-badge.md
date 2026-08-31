# 2026-08-31 — Financial status on the plan card (canceled ≠ expired)

## Task

Innocent's platform feedback (II.1.e) names a **Financial Status** taxonomy —
**Current / Grace Period / Expired / Canceled**. Realise it on the plan card so a
member sees exactly where they stand.

## What the reference actually exposes (settles the scope)

There is **no authenticated `myFinancialStatus` query**. `financialStatus`
(`current | grace_period | expired | canceled`) exists in member-client only on
the **pre-login** `purchaseEligibility` funnel — which the native apps don't use
(checkout is web). So inventing a `myFinancialStatus` read would (a) break the
contract and (b) violate "don't invent endpoints."

Where member-client *does* distinguish the states for a logged-in member is
`PaymentAndPlanScreen.tsx`: it maps the **membership `statusCode`** — already on
the wire — to a label + tone (`active`→Active, `past_due`→Payment overdue,
`canceled`→Canceled, `expired`→Expired, `paused`→Paused, else Status
unavailable), and picks "Renews/Ends" from `autoRenew && code !== "canceled"`.
That is the taxonomy, from data we already fetch.

## The gap this closes (member-client #141)

Both apps' plan cards showed a green **"Covered"** badge only when
`entitlement.entitled`, and **nothing at all** otherwise. So a **canceled /
expired / payment-overdue** member — on the one screen they'd open to find out —
saw no status. member-client fixed the same bug in #141 ("a past_due or canceled
member was told their coverage was fine").

## Change (both platforms)

New pure, tested `PlanStatus.of(membership, entitlement)` → `(label, tone)`:

- **Grace first** (entitlement `graceUntil` set) → "Grace period" (warn) — it
  wins over the raw `past_due` code underneath, matching the app's grace model.
- Else by membership `statusCode`: active→Active(ok), trial→Trial(ok),
  past_due→Payment overdue(warn), paused→Paused(warn), canceled→Canceled(off),
  expired→Expired(off); unknown → Active(ok) **only if** entitled, else
  "Status unavailable"(off) — never claim Active for a status we don't recognise.

The plan card now **always** shows this badge (was: only "Covered"). Tones map
to the closed palette (no amber): **ok**→success green, **warn**→gold accent
(the app's attention colour), **off**→muted. Colour is a dot fill, never the
text (R4), so every label stays legible.

Home is unchanged: it collapses non-covered states exactly like member-client's
`HomeScreen` (only `past_due` is called out, as payment-failed). The finer
distinction belongs on the plan card, which is what this does.

## Files

- Swift: `Feature/Account/AccountViewModel.swift` (`PlanStatus`/`PlanStatusTone`),
  `Feature/Account/AccountScreen.swift` (status row + `planStatusDot`); test
  `AttorneyShieldTests/AccountViewModelTests.swift`.
- Kotlin: `feature/account/AccountViewModel.kt` (`PlanStatus`/`PlanStatusTone`),
  `feature/account/AccountScreen.kt` (status row + `planStatusDot`); test
  `feature/account/AccountViewModelTest.kt`.

## Tests

New on both platforms: each status code maps to its own labelled badge; grace
wins over the raw `past_due`; an unknown code never claims Active unless the
entitlement says covered.

- Swift: `AccountViewModelTests` (single-process, iPhone 16 Pro) → **42 tests
  passed**, `** TEST SUCCEEDED **`.
- Kotlin: `AccountViewModelTest` → **BUILD SUCCESSFUL**.

## For Innocent (nice-to-have, not blocking)

We derive financial status from the membership `statusCode` + entitlement grace,
mirroring `PaymentAndPlanScreen`. If the backend later exposes an authenticated
`financialStatus` on the account/entitlement, we can key on it directly — but
nothing is needed today.
