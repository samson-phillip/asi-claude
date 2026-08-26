# Backend — CodePen V6 parity

**To:** mobile (Android + iOS)
**From:** backend
**Date:** 2026-08-26
**Re:** "Backend asks — CodePen V6 parity (native apps)", 2026-08-26
**Environments:**
`https://gateway-dev.attorneyshield.io/query` · `https://member-client-dev.attorneyshield.io`
`https://gateway-uat.attorneyshield.io/query` · `https://member-client-uat.attorneyshield.io`

One of the five was a real API gap and is built. Two were already provisioned before
you asked — on **both** dev and uat. One is a Product decision and the recommendation
is to drop the feature, for a reason the design does not make visible. And **B1 is not
a provisioning gap at all**: `adminDocumentTypeList` returns a populated list on dev
today, and the reason your apps see `[]` is in your apps. That one is worth reading
first, because it also explains a class of bug you will hit again.

---

## At a glance

| Your ask | Status |
|---|---|
| **A1** — `sessionTranscript`, or a decision to drop | 🛑 **Recommendation: drop it.** A Test Call is a real attorney consult. With Product |
| **A2** — `updatePaymentMethod` | ✅ **Built and deployed** — dev + uat |
| **B1** — seed document types | ⚠️ **Premise disproved.** Types were already seeded on both envs. Your `[]` is an auth error your client swallows. A *different* real gap found and fixed |
| **B2** — enable Stripe + publishable key | ✅ **Already enabled** on dev *and* uat. Read it from `stripePublishableKey`, never hardcode |
| **B3** — dev registration/plans URL | ✅ `https://member-client-dev.attorneyshield.io/plans` (uat below) |

Two things you did not ask about but will trip over are at the bottom. One of them
explains why every incident tile is the same colour.

---

## 1. B1 — the types were always there; your client is hiding an auth error

Taking this first because it is the ask you flagged as blocking, and the fix is on
your side.

`adminDocumentTypeList` does **not** return empty on dev. Run against
`gateway-dev.attorneyshield.io/query` with a member token this morning:

```
### claire-member@attorney-shield.com
  count = 11
   - contract | Contract | active True
   - form | Form | active True
   - guide | Guide | active True
   - policy | Policy | active True
   - incident_report | Incident Report | active True
   - contract2 | contract 2 | active False
   - extra documents | Extra books | active False
   - DRIVERS_INFO | Driver's Information | active True
   - HEALTH_INFO | Health Information | active True
   - GUN_INFO | Gun Information | active True
   - CITIZENSHIP_INFO | Citizenship Info | active True
```

All four Glovebox sections — Driver's, Health, Gun, Citizenship — with icons, active,
and with fields behind them:

```
  CITIZENSHIP_INFO   Passport[file], Birth Certificate or Visa[file]
  DRIVERS_INFO       Issuing State[dropdown], Driver's License[file], Insurance Information[file]
  GUN_INFO           Gun Owner[dropdown], Gun Permit[file]
  HEALTH_INFO        Health Conditions[text], RX Copies[file]
```

### Why you saw `[]`

Without a valid token the query does not return an empty list. It returns an error and
a **null**:

```
### no token at all
  errors: ["unauthorized"]
  data.adminDocumentTypeList = null

### garbage bearer token
  errors: ["unauthorized"]
  data.adminDocumentTypeList = null
```

And both apps turn that null into an empty list before any of your code can see it:

- `kotlin/.../core/network/DocumentModels.kt:135` —
  `val adminDocumentTypeList: List<GqlDocumentType> = emptyList()`
- `swift/.../Core/Network/DocumentModels.swift:130` — `[GqlDocumentType]?`, then
  `?? []` at `AsiApi.swift:359`

So **"my token expired" and "the admin has configured nothing" are the same value in
your app.** That default is why B1 was filed as a provisioning gap: the evidence for
"nothing is seeded" and the evidence for "I am not authenticated" are identical.

This is not specific to document types — it is the shape of every list accessor in
both `AsiApi` files. Worth separating `null` (call failed) from `[]` (call succeeded,
nothing configured) at the transport layer once, rather than per screen. The empty
state the design draws for a configured-but-empty Glovebox is a different screen from
"you have been signed out", and right now neither app can tell which to show.

### The gap that *was* real, and is now fixed

While disproving the premise: **uat had six of the nine fields, not nine** — and the
three missing ones were exactly the three that are not file uploads.

| Document type | Field | Type | dev | uat (before) |
|---|---|---|---|---|
| `DRIVERS_INFO` | `state_of_issue` | dropdown "Issuing State" | ✅ | ❌ |
| `GUN_INFO` | `gun_owner` | dropdown "Gun Owner" | ✅ | ❌ |
| `HEALTH_INFO` | `health_conditions` | text "Health Conditions" | ✅ | ❌ |

So on uat, 14A–14D would have rendered as four upload boxes with none of the questions
the CodePen draws. Only the non-file fields were missing, which is why nobody's
file-upload smoke test caught it — and uat is the QA environment, so it would have
reached you as a QA defect against your build rather than as missing data.

Also fixed in the same migration:

- **"Issuing State" held six options** — `AL, AK, AR, AZ, CA, CO`. That is the alphabet
  cut off, not a decision: a member licensed anywhere else had nothing to pick. Now all
  50 states + DC. Still 2-letter USPS codes, deliberately — members have already
  answered with codes (`AL`, `CA` on dev) and switching to full names would orphan
  those answers.
- **`contract 2` and `Extra books` are deactivated on uat too.** They were dev test
  junk, retired on dev back in `20260813b` (that file is DEV ONLY because it also seeds
  a named test member). On uat they showed as two real Glovebox sections with no fields.

**db #63/#64**, applied to dev and uat and verified: both now return the same nine
fields. Nothing for you to do — re-run your query and the dropdowns appear.

Live on uat, signed in as `paul+daniel.wynn@attorney-shield.com`:

```
adminDocumentTypeList: 13 rows, 11 active
   - contract, form, guide, policy, incident_report
   - DRIVERS_INFO, HEALTH_INFO, GUN_INFO, CITIZENSHIP_INFO
   - AGREEMENT, OTHER
fields on the four identity types:
   DRIVERS_INFO       Issuing State[dropdown]{51 opts}, Driver's License[file], Insurance Information[file]
   HEALTH_INFO        Health Conditions[text], RX Copies[file]
   GUN_INFO           Gun Owner[dropdown]{2 opts}, Gun Permit[file]
   CITIZENSHIP_INFO   Passport[file], Birth Certificate or Visa[file]
```

One thing we deliberately did **not** touch: `AGREEMENT` and `OTHER` exist on uat only,
are global (no country rows, so they show everywhere), and have **zero fields** — they
will render as two empty sections. They look like they were created through the admin
panel during the UAT pass rather than seeded, so we left them for whoever made them
rather than deactivating someone's deliberate test data. If they are in your way, say so
and we will retire them.

### One caveat that will bite you: country scope

`adminDocumentTypeList` is narrowed by country, and when you send no `countryISO2` — as
both apps currently do — the narrowing comes from **the member's own profile country**.

Today's coverage:

| | KE | US | UG | CA | GB | ZA |
|---|---|---|---|---|---|---|
| **dev** doc types | 9 | 9 | 1 | 0 | 0 | 0 |
| **uat** doc types | 9 | 9 | 0 | 0 | 0 | 0 |

So a member whose profile country is Canada, the UK or South Africa gets a genuinely
empty Glovebox — and on uat, so does a Ugandan member. That is real data, not a bug in
the query: it is the known CA/GB/ZA tagging gap, and which countries the four identity
types belong in is a business call, not one we should make in a migration. It is raised
with them alongside A1.

**For your own testing, use a member whose profile country is US or KE** — e.g.
`claire-member@attorney-shield.com` on dev, `paul+daniel.wynn@attorney-shield.com` on
uat. Note `paul+grace.oduya@attorney-shield.com` on uat is a **UG** profile and will
show you an empty Glovebox correctly.

Worth knowing: the same country rule governs `adminIncidentTypeList`, so a CA/GB/ZA
member also sees no incident tiles. member-client already has a distinct empty state
for that ("No incident types are available in *<country>* yet") rather than the
generic one — worth copying, because an unexplained empty grid reads as a broken app
and there is nothing the member can do about it from that screen.

---

## 2. A2 — `updatePaymentMethod` is built

Shipped to dev and uat (**finance #105**, schema column in **db #63**).

```graphql
mutation UpdatePM($org: ID!, $pm: ID!, $input: UpdatePaymentMethodInput!) {
  updatePaymentMethod(organizationID: $org, paymentMethodID: $pm, input: $input) {
    id brand last4 expMonth expYear billingPostalCode isDefault
  }
}

input UpdatePaymentMethodInput {
  expMonth: Int            # 1-12
  expYear: Int             # 4-digit; a 2-digit year off the card is accepted as 20YY
  billingPostalCode: String
}
```

`PaymentMethod.billingPostalCode` is new and readable from `myPaymentMethods` too, so
33D can show the stored ZIP before the member edits it.

**`organizationID` comes first**, not the shape you proposed — it matches
`setDefaultPaymentMethod` and `detachPaymentMethod`, which you already pass it to.

### Semantics worth building against

- **Omitted means unchanged.** Only fields you send are written. Do not send
  `expMonth: 0` for an untouched field — a zero expiry would clear a working card at
  Stripe, and the member would find out at the next renewal rather than at save time.
- **An empty string clears the postal code.** `billingPostalCode: ""` is a deliberate
  clear; omitting the key keeps what is stored. If your form binds an empty text box to
  `""`, you will clear the member's ZIP on an expiry-only save. Send `null`/omit.
- **The card number is not editable.** A different number is a different card:
  `createSetupIntent` + `attachPaymentMethod`. Your shipped "Replace with a new card"
  interim is the right flow and stays the right flow.
- **The response is authoritative.** The row is written from what Stripe confirms, not
  from your input — so render the returned object rather than your local edit. Expiry,
  brand and last4 come back refreshed.

### Errors, with codes to switch on

| `extensions.code` | Message | When |
|---|---|---|
| `PAYMENT_METHOD_NOT_FOUND` | That payment method could not be found. | No such card, **or not the caller's** — deliberately the same answer, so the error cannot confirm an id exists |
| `PAYMENT_METHOD_NOT_EDITABLE` | This payment method can't be edited. Add a new one instead. | M-Pesa and anything else with no expiry to reissue |
| `CARD_EXPIRY_IN_PAST` | That expiry date has already passed. | Rejected by us, not Stripe — Stripe accepts a past expiry because an expired card is a legitimate state |
| `CARD_EXPIRY_INVALID` | Enter a valid expiry date. | Month outside 1-12, or a year that is not a year |

On `CARD_EXPIRY_IN_PAST`: a card expires at the **end** of its stated month, so the
current month is still valid. If you validate client-side, match that or you will
reject a card that works.

M-Pesa methods appear in the same wallet list, so gate the Edit affordance on
`type == "card"` rather than waiting for the error.

### Verified live on dev, against a real Stripe test card

`claire-member@attorney-shield.com` now has a saved Visa ••••4242 on dev for you to
point 33D at.

| Input | Result |
|---|---|
| `{billingPostalCode: "94107"}` | zip set, expiry untouched |
| `{expMonth: 11, expYear: 2031}` | expiry changed, **zip survived** |
| `{expMonth: 3, expYear: 2032, billingPostalCode: "10001"}` | both changed |
| `{expMonth: 1, expYear: 2020}` | `CARD_EXPIRY_IN_PAST` |
| `{expMonth: 13, expYear: 2032}` | `CARD_EXPIRY_INVALID` |
| `{expMonth: 6, expYear: 33}` | accepted as 2033 |
| `{billingPostalCode: ""}` | cleared |
| `{}` | no-op, nothing written |

And `colt-member` attempting to edit `claire-member`'s card:

```
That payment method could not be found. | code: PAYMENT_METHOD_NOT_FOUND
claire's card afterwards: unchanged
```

---

## 3. A1 — recommendation is to drop "View transcript"

You offered the two branches and asked for one. **Take the second: drop it, and match
`member-client` by showing the encounter location.** Here is the part the design does
not make visible.

**A Test Call is a real attorney consult.** It is not a self-test against a canned
video. `admin_incident_types` holds a row with `code = 'Test Call'`, `sort_order 1`,
and the member home renders it as an ordinary tile that calls the same `start()` path
as Traffic Stop or Auto Accident — routed to a live attorney through
`POST /api/vonage/video/member-call` like anything else. The only thing distinguishing
it is its name.

So keeping the transcript link "only on Test Call rows" does not narrow the exposure at
all. It is the same two parties and the same content as any other consult, in text
instead of audio — and MOBILE #140, confirmed by the business, is that members do not
get session recordings. The reasoning behind #140 applies to a transcript with equal
force; the format is not what #140 was about.

Two supporting facts:

- **There is no transcript anywhere to return.** The database has `call_recordings` and
  `video_recordings` and no transcript table. The one thing that produces consult text
  is the real-time subtitle pipeline (Vonage Audio Connector → AWS Transcribe →
  `sendSignal({type:"asr"})`), which is deliberately ephemeral and edge-translated —
  nothing is persisted server-side by design. `sessionTranscript` is not an API gap over
  existing data; it is a new store, a retention policy, and a privilege review.
- `historyApi.ts:75` is not a stale comment. `getCallRecordings()` was removed outright
  rather than flagged off, specifically so no presigned URL could reach a device by
  accident.

**Raised with Product** for the sign-off you asked for. Until they answer, build screen
32 as `member-client` does — outcome badge plus location (`EncounterMap`) — which is
also the only version that has data behind it.

**If what the business actually wanted was "let the member confirm the test call
worked"**, that needs no new API. `commsCallsByMember` already returns
`status endReason answeredAt endedAt`, which is enough for "Connected · 42s" or "No
attorney answered". Say the word and we will spell out the mapping; `callOutcome()` in
`member-client/src/lib/historyApi.ts` already does exactly this and is worth porting
rather than reinventing — the four outcome labels are the business's own wording.

---

## 4. B2 — Stripe is already on, in both environments

Verified tokenless against both gateways this morning:

```
dev  stripePublishableKey -> 'pk_test_51TutVmAFH…' (len 107)
uat  stripePublishableKey -> 'pk_test_51U7EeCAAB…' (len 107)
```

Separate Stripe test accounts per environment — note the keys differ, so a key captured
from dev will not work against uat.

**Read it at runtime from the public GraphQL field. Do not hardcode it and do not bake
it into a build config:**

```graphql
query { stripePublishableKey }
```

It is allowlisted in finance's public-field list, so it works **pre-login** — which is
what the pre-login checkout funnel needs. It is sourced from `STRIPE_PUB_KEY` in the
`asi/<env>/config` secret, which is why it is a field and not a build variable: baking
it in would mean one binary per environment, and your build channel would silently
decide which Stripe account a member's card lands in.

`""` back from the field is the honest signal for "card entry isn't available here" —
render that state rather than handing an empty key to the SDK.

The Stripe mobile SDK is yours to add, as you said. For reference, member-client uses
Stripe **Elements** rather than its own PAN inputs because Stripe hard-refuses raw-PAN
tokenisation with a publishable key outside their own UI
(`"This integration surface is unsupported for publishable key tokenization"`), and it
keeps ASI in PCI SAQ A. The native equivalent is `PaymentSheet` / `CardInputWidget` —
please don't build your own card-number field.

---

## 5. B3 — storefront URLs

| Env | Register / plans hand-off |
|---|---|
| **dev** | `https://member-client-dev.attorneyshield.io/plans` |
| **uat** | `https://member-client-uat.attorneyshield.io/plans` |

Both verified HTTP 200 this morning. Same host as the member web app — the storefront is
served same-origin from it, which is why `App.tsx` has only the path.

An account created there is visible to a dev app pointed at `gateway-dev`, since it is
the same database behind both.

---

## 6. Two things you did not ask about

### Incident type codes are not snake_case — your emoji maps never match

`AsiConfig.kt:63-67` and `AsiConfig.swift:48-52` key their fallback emoji on
`"traffic_stop"`, `"auto_accident"`, `"test_call"`. The live values in
`admin_incident_types.code` are:

```
Test Call · Traffic Stop · Domestic · Auto Accident · Pedestrian Stop · Other · Employment · Family
```

Title Case, with spaces. So **every lookup misses and every tile gets the generic
fallback.** member-client has the identical bug in `lib/config.ts` (`INCIDENT_VISUALS`
is keyed the same way), and there it is more visible: the per-type tint and glow come
from that map regardless of whether an icon is configured, so all tiles render the same
gold instead of the per-type colours the CodePen specifies. The `test_call` equality
check that marks the featured tile never fires either.

Either normalise before lookup (lowercase, spaces → underscores) or key on the icon the
admin configured. Note `code` is admin-editable free text and is now only unique
*within a country* — so treat it as a display/matching hint, never as a stable
identifier. Use `id`.

### Document types can duplicate by design

You will see two active `Traffic Stop` incident types on dev. That is correct, not
corruption: uniqueness is per-country now, and those two carry non-intersecting country
sets (`UG` vs `KE,US`). A member sees only the one for their country. Don't dedupe by
`code`.

---

## What changed on the servers

| Repo | PR | What |
|---|---|---|
| `db` | #63 → #64 | `payment_methods.billing_postal_code`; Glovebox field parity + full state list + uat test-type cleanup |
| `finance` | #105 | `updatePaymentMethod`, `PaymentMethod.billingPostalCode`, `Adapter.UpdateInstrument` |
| `finance` | #106 | `CARD_EXPIRY_INVALID` — the one rejection that had no code |
| `finance` | #107 | the same two, promoted to **uat** |

Running now: `finance:dev-112` and `finance:uat-113`, both verified against a real Stripe
test card — on uat as `paul+daniel.wynn@attorney-shield.com`, whose live membership card
took the expiry-only edit with its postal code intact.

Nothing needs a client release to pick up the B1 data fix — it is data.

The federated schema is live on both gateways; `PaymentMethod.billingPostalCode` and
`updatePaymentMethod` are introspectable now. Note the gateway hot-reloads subgraph
schemas on a ~60s poll, so if you introspect within a minute of a backend deploy you can
see the old schema — that is the poll, not a missing deploy.

## Still open, and with whom

- **A1** — Product: drop "View transcript" from 32, or commission a transcript store
  with a retention and privilege decision. Our recommendation is to drop it.
- **Country coverage for the four identity document types** — business: CA, GB and ZA
  have no document types or incident types at all, and Uganda has none on uat. Which
  countries these belong in is their call. Until then, test with a US or KE member.
