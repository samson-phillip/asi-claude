# 2026-08-19 — Payment method: the real 33D inline-edit

## Task

Backend shipped `updatePaymentMethod` (finance #105), so the CodePen **33D**
inline-edit — edit expiry + billing ZIP without re-entering the card — is finally
buildable. It was the design all along; we'd only shipped the card-graphic +
"Replace" interim *because* the API was missing. Build it. Repos: `kotlin`,
`swift`, this one.

## Shipped

The Payment method screen now carries, below the card graphic: an **Expiration**
and a **Billing ZIP** field, the reference's note ("Update the expiration date or
ZIP without re-entering the card…"), a **Save changes** button, and **"Replace with
a new card ›"** demoted to a text link (the replace path stays for a new number).

- **API** — `updatePaymentMethod(organizationID, paymentMethodID, input{expMonth,
  expYear, billingPostalCode})` on both `AsiApi`s, returning the authoritative
  `PaymentCard`. `PaymentMethod.billingPostalCode` added to the model + the
  `myPaymentMethods` query so the stored ZIP pre-fills.
- **Semantics honoured** (per finance #105):
  - only *changed* fields are sent; unchanged ones are **omitted** (never `0`,
    which would clear a working expiry at Stripe);
  - an empty ZIP is sent as `""` only when it actually changed — a save that only
    touches expiry omits the ZIP key, so it can't wipe a stored ZIP;
  - the **response is authoritative** — the card and the form are reset from what
    the mutation returns, not the local edit;
  - rejections surface the backend's own member-facing message
    (`CARD_EXPIRY_IN_PAST` / `_INVALID`, `PAYMENT_METHOD_NOT_EDITABLE` /
    `_NOT_FOUND`), since `gql` throws with the GraphQL `message`.
- **Validation** — expiry parsed from "MM/YY" (2-digit year → 20YY); month 1-12; a
  half-typed expiry disables Save and marks the field. Past-expiry is left to the
  backend (a card is valid through the end of its stated month).
- The card number stays uneditable — a different number is "Replace with a new
  card" (Stripe `attachPaymentMethod`), exactly as backend advised.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — build | **BUILD SUCCEEDED** |

Not yet driven on-device; backend left a live card to test against —
`claire-member@…` on dev has a Visa ••••4242 with `updatePaymentMethod` verified
server-side.

## Also this session (from the backend response)

- **B3** — `planUrl` corrected to the real dev storefront
  `member-client-dev.attorneyshield.io/plans`.
- Recorded the backend response in
  [[2026-08-26-backend-codepen-parity-response]]. Still open: **A1** (Product to
  drop "View transcript" — recommended; Activity should add outcome labels via
  `commsCallsByMember` instead), **A3** (sensitive-field flag for Glovebox
  masking), and **B1**'s real lesson — our list accessors turn an auth-error
  `null` into `[]`, so "signed out" looks identical to "nothing configured";
  worth separating at the transport layer.

## Next

Account parity (Family dashed spot-cards, Settings pane, hub email), Home (drop
the non-design extras, heading/link, grace state — keep the 2-col tiles),
Notifications (split), Activity (outcome labels per A1).