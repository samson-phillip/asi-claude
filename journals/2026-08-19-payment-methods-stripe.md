# 2026-08-19 — Payment methods: pulling the reference forward, Stripe plan, Stage 1 API

## Task

Add a card-update path to Payment & plan. It turned into: pull the much-changed
`member-client` reference, learn how payments now work there, and start a staged
native build. Repos touched: `member-client` (reference, branch switched),
`kotlin`, `swift`, `asi-claude`.

## The reference had moved a long way

`member-client` was still on `main` (the old login/tiles/call app). The live
reference is **`origin/dev` — 193 commits ahead** — with a full payment stack and
much else (guest flows, country/timezone detection, billing org-scoping, routing
changes). Switched the local checkout to `dev`; it is the new behavioural
baseline and a lot beyond payments will want reconciling later.

## What the reference does for cards (and what the screenshot got wrong)

The supplied screenshot (33D) showed inline expiry/ZIP editing. That design is
**dead**: there is still no `updatePaymentMethod` and no billing-ZIP field. The
resolved flow is a **Payment Methods manager** (`SavedCardsScreen`):

- a card carousel, a "your cards" list with **Make default** and **Remove**,
- sub-account and empty states,
- an **Add card** screen using **Stripe Elements** — card data goes straight to
  Stripe (`createPaymentMethod` → `pm_…`), and only that opaque id is sent on via
  `attachPaymentMethod`. `createSetupIntent` is a best-effort handshake.

The publishable key comes from the backend (`query stripePublishableKey`), empty
when the environment isn't configured — so nothing secret needs handing over, and
card entry degrades to an "unavailable" state on its own.

## The plan (user-approved)

Card entry needs the **Stripe mobile SDK** on both platforms — a real dependency
decision, which the user made ("integrate Stripe"). Because it is large and the
add-card half can't even be tested without a Stripe-configured dev environment,
it is staged:

- **Stage 1a — the API layer** — `setDefaultPaymentMethod` and
  `detachPaymentMethod`, matching the reference's `paymentApi.ts` (return whether
  the write took; a failure is a surfaced toast, not a thrown error). Added to
  both `AsiApi`s with their response models. `myPaymentMethods` list already
  existed. **Done.**
- **Stage 1b — the manager screen** — a new `AccountPane.PaymentMethods` /
  `.paymentMethods`: cards listed as bordered cards (brand · last4, expiry, a
  green **Default** badge, gold border on the default), with **Make default** and
  **Remove** (removal behind a confirm), plus sub-account and empty states. The
  Payment & plan "Payment method" row now carries a **Manage** action that opens
  it, and the Account title bar names it. The per-card busy state spins the row
  in flight. **Done.**
  - **No Add button yet** — adding a card is Stage 2 (Stripe), so the empty state
    reads plainly rather than dangling an add affordance that cannot work. A
    member with no cards sees a benign dead-end until Stage 2; the common case
    (cards already attached) is fully functional.
  - **Cardholder name** is a "Cardholder" fallback for now — `billingName` is not
    yet fetched into the native `PaymentCard`; a small follow-up.
- **Stage 2 (next): the Stripe SDK + Add Card** — native card field → token →
  `attachPaymentMethod`, with the "not configured" fallback.

## An operational incident

The dev disk hit **100% full** mid-task — even the shell could not capture
output. Cleared it by deleting rebuildable artefacts only (Gradle/`app/build`
outputs and Xcode DerivedData), which freed ~11 GiB. Nothing user-authored was
touched; the next build is a clean one. This is the low-disk risk from
`open-concerns.md` finally biting — it needs a real fix, not just reclaiming
build caches.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` (API + manager) | **BUILD SUCCESSFUL**, all pass |
| iOS — `AccountViewModelTests` (compiles the API + manager) | **8 / 8 passed**, 0 failed |

## What was pushed first

The five completed design changes (Home tiles, Glovebox upload well / title bar /
watermark+subtitle, Payment & plan) were committed and pushed before starting
Stripe, so the payment feature builds on a clean base:
`kotlin be2808e`, `swift eb36ffe`, `asi-claude 0bc4c24`.

## Addendum — the screen pivoted to CodePen 33D's look

Shown the CodePen 33D screenshot again, the ask was to make the app's payment
screen *look* like it. 33D is the single-card layout: a card graphic, a note,
and "Replace with a new card". Chosen resolution: **build 33D's look, honestly**
— keep the pieces that can work, drop the ones that can't.

- The Stage-1b **manager** (multi-card list with make-default / remove) is
  **replaced** by the 33D single-card screen: a `CardGraphic` (brand, an Active
  status, •••• last4, cardholder, EXP) + an `AsiInfoChip` + a **Replace with a
  new card** button. Empty and sub-account states kept.
- **The inline expiry/ZIP edit + Save is not built** — no `updatePaymentMethod`,
  no billing-ZIP field, so those would be a Save that cannot save. Left off.
- **Replace routes to a new `AddCard` pane**, which for now states plainly that
  card entry isn't in the app yet (Stage 2 fills in the Stripe form). Not a dead
  button — it opens a real, honest screen.
- **make-default / remove stay in the API and view model** (`setDefaultPaymentMethod`,
  `detachPaymentMethod`, `makeDefaultCard`, `removeCard`) for a future multi-card
  view; the single-card 33D screen just does not surface them.
- **"Active" and "Default" are green *fills*, never green text (R4)** — a dot
  plus the word, as the CodePen's green status is not a legible text colour on
  dark under the palette.

Verified again: Android `testDebugUnitTest` **BUILD SUCCESSFUL**; iOS
`AccountViewModelTests` **6/6**.

## Open / next

1. **`billingName`** — now fetched (`myPaymentMethods { … billingName }`) into
   `PaymentCard` and shown as the cardholder on the card graphic, falling back to
   "Cardholder". **Done.**
2. **Stage 2 Stripe SDK** — needs the SDK added to both apps and a
   Stripe-configured dev environment (the `stripePublishableKey` must return a key)
   to test add-card.
3. **Broader reference drift** — `member-client` dev is 193 commits ahead; a lot
   beyond payments (guest flows, country detection, routing) may need reconciling.
4. **Dev disk** — chronic; reclaiming build caches is a stopgap.