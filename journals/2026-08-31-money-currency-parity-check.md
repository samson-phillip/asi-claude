# 2026-08-31 — Money/currency parity check against member-client

## Task

Second parity pass (after call-flow). Audited the **money/currency** theme of the
member-client pull (`ab9f8ed` → `127ea35`) against kotlin + swift.

## What changed in member-client (money-relevant)

| Commit | Change | Mobile status |
|---|---|---|
| `b74ded8` | "Never quote a plan in money the shopper cannot pay in (#136)" — `PlansScreen.priceForPeriod` no longer falls back to `inPeriod[0]` (any price, any currency); the fallback is restricted to the currencies the shopper's payment rails accept, else the card drops. Fixed a US member being offered a UGX-only global plan at "UGX 60,000/mo". | **N/A (no mobile analog).** Mobile has **no storefront**: it never lists products or lets the member pick a currency. The plan price comes from `myMembership` — the member's already-selected plan, one price per line in a single server-resolved currency (`AsiApi.getMembership`). There is no `priceForPeriod` currency fallback to get wrong. |
| `1d5e240` (money.ts) | Added `periodWords()` — long per-period prose ("per month") for the **web checkout consent sentence**, because both web checkouts built that wording from the price *suffix* and got it wrong ("per mo" / "$16.00/mo charge"). | **N/A (web-only); mobile already correct.** Mobile has no web-style consent line built from a suffix. Its charge copy is prose ("…your card on file is charged today"), and its cadence line already spells the period out — `billedCadence` → "billed monthly / yearly / weekly" on both platforms. |

So the two recent money commits require **no port**.

## The fix found while checking — zero-decimal currencies

Comparing member-client's `money.ts formatMoney` (unchanged recently, but the
behavioural authority) against mobile's `formatMoney` surfaced a real divergence:

- member-client uses `Intl.NumberFormat({style:"currency"})`, so **zero-decimal
  currencies render without a fraction** — the ISO set (UGX, JPY, …) via CLDR, and
  **KES explicitly** (its code names KES as the example). A Kenyan price reads
  `KES 60,000`.
- mobile's `formatMoney` always divided by 100 and forced two decimals, so the
  same amount read **`KES 60,000.00`**.

This matters here: the app bills Kenyan members via **M-Pesa** (the STK/`past_due`
settlement rail is already implemented), so KES is a live currency, not
hypothetical.

**Fix:** both `formatMoney`s now carry a zero-decimal currency set (the ISO 4217
zero-decimal list **+ KES**, mirroring member-client) and drop the fraction for
those, so `KES 60,000` / `UGX 60,000` / `JPY 5,000` read correctly and `formatRate`
inherits it (`KES 60,000/mo`). Two-decimal currencies (USD, GBP, EUR) are
unchanged.

Deliberately **not** changed: mobile renders non-USD as a **code**, not a symbol
(`GBP 38.00`, not `£38.00`) — a documented, unit-tested choice. member-client shows
the Intl symbol. Aligning that is a visual decision for the team, flagged rather
than made unilaterally; this pass only fixed the decimal-count correctness bug.

## Files

- `swift/AttorneyShield/Core/Format/Formats.swift`, `FormatsTests.swift`
- `kotlin/app/.../core/format/Formats.kt`, `FormatsTest.kt`

## Tests

- Swift: `-only-testing:FormatsTests` (single-process, iPhone 16 Pro) →
  **15 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `./gradlew testDebugUnitTest --tests …FormatsTest` → **BUILD SUCCESSFUL**.

## Branching

First work under the new branch model: committed to **`dev`** on both repos (swift's
integration was moved from `main` → `dev` this session so both apps match). `uat` /
`prod` untouched — those advance only on an explicit release, with tags.

## Open decision

Whether to align mobile's non-USD rendering to member-client's **symbols** (`£`,
`KSh`, `¥`) instead of currency codes. It's a deliberate tested choice on mobile, so
left for the team to call.
