# Backend gaps and blockers

Running register of what the mobile apps need from the backend.

**Status key:** BLOCKING = stopped now · HIGH = blocks a phase · LATER = needed,
not urgent.

Last updated: 2026-08-17, after guest sign-up was confirmed end to end
against the live gateway (see §9).

---

## Correction: most of this list was wrong

Earlier versions claimed registration, the document vault, family sub-accounts,
notifications, OTP sign-in and token refresh had no endpoints. **They all exist.**

The error was ours: we inferred the API surface from the operations
`member-client` happens to use, rather than asking the gateway. It has **238
queries and 297 mutations** and introspection is enabled at
`https://gateway-dev.attorneyshield.io/query`.

Lesson worth keeping: introspect the schema before concluding anything is
missing.

---

## Resolved

| Item | Resolution |
|---|---|
| GraphQL gateway URL | `https://gateway-dev.attorneyshield.io/query` — was in `lfr-desktop/.env.example` all along |
| Dev member account | Supplied; sign-in verified end to end on Android |
| Token refresh | `refreshToken(input: RefreshTokenInput)` |
| OTP sign-in | `requestLoginOtp(email, channel)` / `verifyLoginOtp(email, code, countryISO2)` |
| Registration 10–12 | `updateMyProfile` (DOB/gender/address), `createUserAddress`, `setMemberPin`, `memberPinStatus` — **built and verified on device**. 08/09 blocked, see §4 |
| Date format | `dateOfBirth` must be `YYYY-MM-DD`; the gateway says so in the error |
| `Gender` enum | `male`, `female`, `other`, `non_binary`, `unspecified` (lower-case) |
| States/provinces | `subdivisionsByCountry(countryId:)` returns all 50 US states |
| Document vault | `createUserDocument`, `deleteUserDocument`, `adminDocumentTypeList`, request/finalize upload pattern |
| Family / plan / payment | `addSubaccount`, `changeMembershipSeats`, `changeMembershipPlan`, `attachPaymentMethod`, `createSetupIntent` |
| Notifications | `notificationList`, `markNotificationRead`, `markAllNotificationsRead`, `clearNotifications`, `registerWebPush` |
| Emergency contacts | Full CRUD |
| Activity | `biMemberActivity` |

---

## Still open

### 1. Dev data is not seeded — BLOCKING

**Corrected 2026-08-13.** We previously said no countries were configured. Wrong:

- `countries` → `[]`
- `country(id: f989d06a-…)` → **United States, `US`**
- `subdivisionsByCountry(<that id>)` → **all 50 states + DC**

The data exists; the **`countries` list query** is what returns empty. We read
the country from the member's profile instead, which works and is arguably more
correct, but the list query is broken.

**Genuinely still empty:** incident types (retested authenticated, with and
without a country filter) and languages (only `ar-SA`, not default).
`casesByUser` is also empty.

**Need on dev:** `countries` fixed, incident types seeded with translations, an
English language entry marked default, and a case for the test member.

### 2. No attorney has ever been online — OURS TO ARRANGE, not a backend ask

`member-call` returns `409`. Going online is
`commsUpsertAttorneyQueueMember(queueId, attorneyId, role, weight)`, with a wider
presence model behind it (`attorneyPresence`, `attorneyActiveSession`,
`attorneyDevice`).

**We are handling this ourselves** by running `lfr-desktop` — it is a desktop app
and that is what it is for. Not on the backend list.

### 3. Shape confirmations — HIGH

**Three of these are now answered** (introspection + the deployed JS bundle,
2026-08-13):

- `OtpChannel` = `EMAIL` | `SMS`
- `verifyLoginOtp` returns `LoginPayload` — the same shape as `login`
- `countryISO2` is **optional**; the web client sends `null`

Still open: what `countryISO2` is actually for; access-token lifetime and
whether refresh rotates; whether `verifyMemberPin` is the intended server-side
gate for ending a call; the casing inconsistency.

Also learned: the gateway **does not enumerate accounts** — an unknown address
returns `sent: true` with the submitted address masked back. Good behaviour, but
it means the design's guest-mode branch cannot detect an unrecognised email at
sign-in.

And: **one device may be signed in at a time** (`otherSessionsRevoked`,
`mySessionStatus` → `another_device`).

### 4. Genuinely absent from the schema — HIGH

Nothing here is worked around with a placeholder; the feature is left unbuilt and
listed, so it cannot be forgotten.

- **Phone capture and verification** (screens 08, 09). `updateMyContactInfo` can
  *store* `phoneE164`, but nothing sends or checks a phone code, and
  `phoneVerifiedAt` is admin-only. `requestLoginOtp(channel: SMS)` is a sign-in
  code to an already-verified phone, so it cannot verify a new one. **Both
  screens omitted** rather than shipping the entry half with its "we'll text you
  a code" promise reworded away.
- **Pronouns** (screen 10). No pronoun field on any input type, schema-wide. The
  input is absent rather than collected and dropped.
- **Situation preferences** (13B, 13C, 27B). No `situation` / `preference` /
  `favourite` operations. Home shows the full list because there is nowhere to
  store a choice.
- ~~**Trial and guest** (V1–V2, T1–T8, G1–G3). No `trial` / `guest`
  operations. Is a guest a real account with a role, or local-only state?~~
  **Guest is now answered — see §9 (2026-08-16).** A guest *is* a real account.
  Trial is still only half-there: `convertMyTrial` ends one, but nothing in the
  schema *starts* one, so T1–T8 stay listed here.

### 5. Deep-link contract — HIGH

Real path and parameter names. We accept `/app/return`, `/return-to-app`, `/app`
with an `email` parameter, confined to one file. The link must not carry a
credential — we treat it as untrusted input.

### 6. Domain verification files — HIGH (web task)

`assetlinks.json` and `apple-app-site-association` on both hosts, for
`com.app.attorney.shield`. Blocked on us producing a release keystore first.

### 7. `member-call` has no authentication — LATER

Anyone can place a call against any org/member ID they can guess, and it routes
to a real attorney. Flagged, not designed around.

### 8. Error/danger colour — LATER (Blue Sky, not backend)

The palette forbids the red it names and supplies no error colour, but the call
flow needs an error state and a hang-up control.

---

## 9. Guest users — SHIPPED on dev, and it unblocks self-serve sign-up

Backend message, 2026-08-16: *"i have added guest user implementation. you can
sign up with a new account and test it in member client."*

Read from the live schema at `gateway-dev.attorneyshield.io/query`. **Not tested
against a real account** — signing up means creating an account and entering
credentials, which is not something I do; that step needs a human or a supplied
test account.

### What actually shipped

There is **no `Guest` type and no separate sign-up mutation.** Guest is a
*segmentation status* on an ordinary member account, and sign-up is folded into
the OTP flow we already use.

**1. `verifyLoginOtp` now provisions the account on first verification.**

```graphql
verifyLoginOtp(
  email: String!
  code: String!
  countryISO2: String
  origin: SignupOrigin      # NEW
): LoginPayload!
```

The gateway's own words: *"On first verification this also PROVISIONS the account
(member self-serve sign-up)."* So **sign-up is request-code + verify-code** —
the same two calls as sign-in. There is no separate registration endpoint to
build.

`enum SignupOrigin { APP, WEB }` records which door a **new** account came
through and sets its starting status: **`APP` → Guest User**, **`WEB` → Member
Lead**. It is *ignored for an account that already exists*, so a Member Lead who
later opens the app keeps the status they were created with. **It defaults to
`WEB`.**

**2. `myAccountStatus` reads the caller's own segmentation.**

```graphql
myAccountStatus: MemberStatusRef   # { code: String!, name: String! }
```

e.g. `guest_user` / `"Guest User"`. Self-scoped — taken from the token, never
from an argument. **Null** when no status is stored (an account provisioned
before the segmentation migration, or one the reconcile pass has not reached);
the gateway's guidance is to treat null as *unknown* and fall back to
entitlement rather than assuming.

Why it exists, per the schema: it separates a **Guest User** (never purchased,
exploring) from a member whose **plan lapsed**. Both are unentitled, so
`membershipEntitlement` alone cannot tell them apart, and they are shown
different things.

### The gap on our side — closed 2026-08-16

Both apps sent `verifyLoginOtp(email, code)` without `origin`. Because it
defaults to `WEB`, an account created from the mobile app was stamped **Member
Lead, not Guest User** — the wrong segment, silently, and unfixable afterwards
from the client since `origin` is only read at creation.

**Both are now done:** `origin: APP` is the API-level default on `verifyLoginOtp`
(every sign-in from this app is from the app, and the gateway ignores it for an
existing account), and `myAccountStatus` is resolved in the same best-effort pass
as the profile and cases, then carried on `MemberContext.accountStatus` and
re-read on refresh so a converted guest stops reading as one.

**Correction to the 2026-08-15 note:** it said both apps already sent
`countryISO2`. They do not — the *query* declares it, but no call site ever
populated it, so it has always gone as null. It is still null, deliberately:
`countryISO2` is stamped as the member's HOME country, which drives products,
currency and billing, and a device locale is not a home country. See question 6.

### What this changes for scope

Development plan §3 lists the CodePen sign-up / payment / trial / guest journey
as **blocked, not merely unbuilt**. That is now partly wrong:

- **Sign-up (G1–G3, and the account-creation half of 08–12): unblocked.** It is
  the OTP flow with one extra argument.
- **Trial (T1–T8): still blocked.** `convertMyTrial(organizationID)` *ends* a
  trial and charges the card; **nothing in the schema starts one.**
- **Payment: unchanged.** Still web Stripe, still the App Store risk in
  `open-concerns.md` §1.

Also relevant and already noted in §3 above: the gateway **does not enumerate
accounts** — an unknown address returns `sent: true` with the address masked
back. So the app still cannot tell a new email from an existing one *before*
verification. With self-serve provisioning that is now a feature rather than a
limitation: one flow serves sign-in and sign-up, and the account simply comes
into being on first correct code.

### Confirmed end to end (2026-08-17)

A brand-new email was taken through the app's own OTP flow on iOS, then the
resulting account was read back by signing into it on Android. The gateway
returned:

```
userId=54b146bb-8a39-4394-be82-62d3f7216b03
roles=[Member]
accountStatus=guest_user / "Guest User"
```

So **`origin: APP` does what it was supposed to**: an account created from the
mobile app is segmented as a Guest User, not a Member Lead. That closes the
central unknown in this section — everything above was written against the
schema, and this is the first time it has been observed from the live gateway.

Three things this settles as a side effect:

- **Self-serve sign-up genuinely works from the app.** No web hand-off, no
  pre-provisioning: the OTP flow creates the account on first correct code.
- **`myAccountStatus` is readable by a plain member** — it is self-scoped from
  the token, so unlike `statusCodeList` it needs no elevated permission.
- **Question 5 is partly answered for new accounts:** a freshly created account
  is stamped immediately, so the null-status fallback is not being exercised by
  new sign-ups. Whether *pre-migration* accounts have been reconciled is still
  unknown.

Note the sign-in code is **4 digits**, not 6.

### Questions for the backend

1. ~~**Is `origin: APP` the whole story for a mobile guest**, or does anything
   else need to be stamped at creation?~~ **Answered by observation** — it
   produces `guest_user`. Still worth a confirmation that nothing *else* ought
   to be stamped at the same time.
2. **What are the status codes?** `statusCodeList` requires a permission members
   do not hold, so the app cannot enumerate them. We need the list — at minimum
   which code means guest, which means lapsed, and which means converted — or a
   member-visible way to read it.
3. **What may a Guest User actually do?** Specifically: can they place a
   `member-call`? Entitlement says no, but the product intent for a guest is
   unclear and it decides what the app shows after sign-up.
4. **How does a guest convert?** No trial-start operation exists, so the only
   path visible from the schema is web Stripe and back.
5. **Are pre-migration accounts being reconciled?** `reconcileMemberStatuses`
   exists; if it has not run over dev, `myAccountStatus` will be null for the
   existing test members and we will be exercising only the fallback path.
   *Partly answered:* newly created accounts are stamped at once, so this is
   now only a question about accounts that predate the migration.
6. **Does the rebuilt registration flow keep `/choose-plans`?** UAT checkout is
   `https://uat.attorney-shield.net/choose-plans` (supplied 2026-08-17), but
   that is the **old** app's plan chooser. Also note the TLD — registration is
   on attorney-shield.**net**, not the `.com` marketing site.
7. **Will UAT carry domain-association files?** The apps claim
   `attorney-shield.com` and `www.attorney-shield.com` only, so a return deep
   link from UAT checkout cannot open the app today.
8. **Should the app send `countryISO2` at sign-up?** It is stamped as the
   member's HOME country and drives products, currency and billing. We can
   detect a device region, but a device region is not a home country — someone
   signing up while travelling would be stamped wrong, permanently as far as the
   client is concerned. We send null until someone rules on it.
