# Backend asks — CodePen V6 parity (native apps)

**From:** Mobile (Android + iOS)
**Date:** 2026-08-26
**Context:** We are building the native apps to the **CodePen "Attorney Shield App V6"**
design (the approved look-and-feel reference). `member-client` is our **API/behaviour**
source, not our visual reference.

Each item below is a place where a **CodePen screen needs a capability that
`member-client`'s own API surface does not provide** — i.e. we cannot wire it from
the shared repo because the operation isn't there (an *API gap*), or it exists but
the test environment isn't provisioned for it (a *provisioning* item).

Everything was checked against `member-client/src` directly; file references are
included so these can be confirmed quickly. The **"Already on us" list at the end**
records the CodePen features we verified *are* supported in `member-client` and are
therefore our own work, not requests — so nothing here is something the repo already
answers.

---

## A. API gaps (a CodePen screen needs an operation `member-client` doesn't have)

### A1 — Session **transcript** retrieval · CodePen screen 32 (Activity)
- **The design:** the Activity timeline shows a **"View transcript ›"** link on Test
  Call rows.
- **What `member-client` has:** nothing. Recording/transcript retrieval was
  **deliberately removed** — `historyApi.ts:75` states *"there is deliberately no
  recording-fetch here… MOBILE #140, confirmed by the business: members do not have
  access to session recordings. The former getCallRecordings() query was removed."*
  Call history there shows the encounter **location** instead.
- **The gap:** to build screen 32 as the CodePen draws it, we need an operation that
  returns a **transcript** for a session (at minimum for **Test Call** sessions, which
  the design explicitly keeps the link on). Suggested shape:
  `sessionTranscript(caseId: ID!) → { text | segments[] }`, member-scoped by token.
- **Decision needed if you can't provide it:** #140 says members get *no* recordings.
  If that stands, the CodePen design is wrong on this point and Product should sign
  off on **dropping "View transcript"** (we would then match `member-client` and show
  location). We need one or the other — the app currently shows neither.

### A2 — `updatePaymentMethod` (edit expiry + billing ZIP) · CodePen screen 33D
- **The design:** the Payment-method screen edits **expiration** and **billing ZIP**
  in place, with **Save changes**, without re-entering the card.
- **What `member-client` has:** `paymentApi.ts` exposes only `listPaymentMethods`,
  `setDefaultPaymentMethod`, `detachPaymentMethod`. There is **no** update/edit
  operation and **no** billing-ZIP field on a saved method anywhere in `lib/` or
  `screens/`.
- **The gap:** to build 33D's inline edit we need
  `updatePaymentMethod(paymentMethodID: ID!, expMonth: Int, expYear: Int, billingPostalCode: String) → PaymentMethod`.
- **Interim (no new API needed):** we currently ship the **card-graphic + "Replace with
  a new card"** variant of 33D — view the card, replace it via the existing Stripe
  attach flow. That needs nothing from you. This ask is only if Product wants the
  literal inline-edit design.

---

## B. Environment / data provisioning (API exists; the test env isn't set up)

### B1 — Seed **incident document types** on the test org · CodePen 31, 14A–14D
- **The design:** the Digital Glovebox (31), the four document sections (14A–D:
  Driver's / Health / Gun / Citizenship), and the "Upload documents" setup step.
- **What `member-client` has:** the full flow — `listDocumentTypes()` over
  `adminDocumentTypeList` (`api.ts:1599`), per-type document fields, and presigned-URL
  upload (`profileApi.ts:163-182`). **The API is complete.**
- **The provisioning gap:** `adminDocumentTypeList` returns **empty** on our dev/test
  org, so no sections can render and there is nothing to upload against. **Please seed
  the standard document types** (Driver's, Health, Gun, Citizenship, with icons) on the
  test org so we can build and demo the Glovebox to the design.

### B2 — Enable **Stripe** on the test env · CodePen 33D "Replace with a new card" / add card
- **The design:** adding or replacing a card via card entry.
- **What `member-client` has:** `createSetupIntent` (`api.ts:1121`) and
  `attachPaymentMethod` (`api.ts:1145`) — the Stripe Elements handshake. **The API is
  complete.**
- **The provisioning gap:** card entry needs the test env's **Stripe publishable key**
  available and Stripe enabled end-to-end. Without it, `createSetupIntent` has nothing
  to hand the SDK and add-card can only reach a "not configured" state. Please
  **confirm Stripe is enabled on the test env and provide the publishable key** (or the
  config path the client should read it from). *(The Stripe mobile SDK itself is our
  dependency to add — not an ask.)*

### B3 — A dev registration/plans URL · CodePen 04 "Choose plan" / Register hand-off
- **The design:** the **Register** button hands off to the web plan/checkout flow
  (CodePen 04–07, the App↔Web handoff).
- **What `member-client` tells us:** its public storefront lives at **`/plans`**
  (`App.tsx`: *"The public storefront lives at /plans"*) and is served same-origin,
  so it carries no absolute host of its own.
- **The ask:** please give us the **registration/plans URL for the dev
  environment** — where the dev `member-client` storefront is deployed — so a dev
  build hands members to a page whose account the dev app can then see. We already
  have the dev gateway/comms hosts; we just need the matching storefront URL.

---

## Already on us — verified supported in `member-client`, so NOT requests

We checked these CodePen features against the repo and confirmed the operations exist;
we are wiring them ourselves and are **not** asking for anything here:

| CodePen screen | Capability | Where it already is in `member-client` |
|---|---|---|
| 34 — PIN to end a call | verify the member's PIN | `verifyMemberPin(userId, pin)` — `memberApi.ts:120` |
| 30A — in-call documents | list the member's own docs mid-call | `listMyDocuments(userId)` — used in `CallScreen.tsx` (#138) |
| 31 / 14x — glovebox upload | list types + presigned upload | `listDocumentTypes` (`api.ts:1599`), `profileApi.ts:163` |
| 08–12 — registration steps | phone verify, profile, onboarding | `registrationApi.ts` (`requestPhoneVerification`, `verifyPhone`, `updateMyProfile`, `completeMyOnboarding`) |
| 33A/33D — cards | list / default / remove | `paymentApi.ts` (`listPaymentMethods`, `setDefaultPaymentMethod`, `detachPaymentMethod`) |

---

## Summary

| # | Ask | Type | Blocks (CodePen) |
|---|---|---|---|
| A1 | `sessionTranscript` — or a Product decision to drop "View transcript" | API gap / decision | 32 Activity |
| A2 | `updatePaymentMethod` (expiry + billing ZIP) | API gap | 33D inline edit (interim shipped without it) |
| B1 | Seed document types on the test org | Provisioning | 31, 14A–D, upload step |
| B2 | Enable Stripe + publishable key on the test env | Provisioning | 33D add/replace card |
| B3 | A **dev** registration/plans URL for the Register hand-off | Provisioning | 04 Register hand-off |

Only **A1** and **B1** actually block demo-path screens. A2 has a shipped interim; B2
gates the add-card path only; B3 supplies the Register hand-off storefront URL for the
dev environment (the `/plans` path is already handled our side).