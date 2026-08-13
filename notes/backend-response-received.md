# Backend response to "Backend asks from the native apps"

**To:** mobile (Android + iOS)
**From:** backend
**Date:** 2026-08-13
**Environment:** `https://gateway-dev.attorneyshield.io/query` · `https://comms-dev.attorneyshield.io`

Thank you for the document. It is the most useful thing anyone has sent this
project — the corrections on your own earlier claims, and the list of screens you
deliberately did **not** ship, saved more time than the asks themselves.

Everything below is either shipped to dev, answered, or has a question back at
you. Where I disagreed with a suggested approach I have said so and why.

---

## At a glance

| # | Ask | Status |
|---|---|---|
| A4 | No *real* case for the test member | ✅ **Shipped** — plus the root cause, which was not seeding |
| A5 | `deleteUserDocument` forbidden for own file | ✅ **Shipped** |
| A6 | Document-field `type` vocabulary | ✅ **Answered** below + dev rows tidied |
| A7 | `addSubaccount` accepts a bogus `seatPriceID` | ✅ **Shipped** |
| A8 | `attorneyAssignments { attorney { … } }` times out | ✅ **Shipped** — as a new field, not a fix to the old one |
| B1 | Phone send/verify | ✅ **Shipped** |
| B2 | Pronouns | ✅ **Shipped** |
| B3 | Situation preferences | ✅ **Shipped** |
| B4 | Emergency-contact notify-by | ✅ **Shipped** |
| B5 | Trial and guest | ❓ **Question back** — needs a product decision, see below |
| B6 | Member-readable transcript | ❌ **Not planned yet** — do not wire the link |
| B7 | Change a card in-app | ✅ **Answered** — the key you need already exists |
| B8 | Notification categories + frequency + `kind` | ✅ **Shipped** + `kind` answered |
| C1–C8 | Eight answers | ✅ **All answered** below |
| D1 | `member-call` takes no authentication | ✅ **Fixed** — ⚠️ **action required from you** |
| E1 | Deep-link contract | ✅ **Confirmed** — your current implementation is the contract |
| E2 | Domain verification files | ⏳ Waiting on your fingerprint + Team ID |

**One thing needs action from you before it bites:** D1. Everything else is
additive.

---

## ⚠️ D1 — action required: send your access token to the comms REST endpoints

You were right, and it was worse than you found.

`POST /api/vonage/video/member-call` took no authentication, and neither did
`GET /api/calls/member-documents` — which returns a member's **identity
documents** (driver's licence, insurance) with presigned URLs, keyed on nothing
but a `callId`. A callId is not a secret; it travels through several clients.

The cause was one line of middleware: identity was attached on `/query`,
`/graphql` and `/` only, so every REST handler was blind **even when the caller
sent a good token**. That is now fixed, and the two handlers check the caller
against the member they are acting for.

### What you need to do

Send the same bearer you already send on GraphQL:

```
Authorization: Bearer <accessToken>
```

on **every** request to `{apiBaseUrl}/api/*`, including `member-call`.

The rule the server applies:

- A member may call **only for themselves** — the token's subject must equal
  `memberUserId`. Staff (support placing a call for someone on the phone) may
  act on a member's behalf.
- No token → `401`. Wrong member → `403`.

### You have a window, but it is not open-ended

Four clients send no header today: yours, the web member-client and the attorney
desktop app. Dev is running with `COMMS_REST_AUTH_MODE=warn`, which logs the
violation and lets the call through, so **nothing breaks for you right now**.

The web client and desktop app are already updated. Once you confirm your builds
send the header, we remove `warn` from dev. `uat` and `prod` enforce from the
start — the variable only permits when explicitly set to `warn`, so there is no
environment where forgetting it leaves the door open.

**Please tell us when your builds send it.**

---

## A. Environment and seeding

### A4 — the test member's cases · shipped, and the cause was not seeding

You read this exactly right — the six cases were yours — but the interesting
part is *why* `partnerID` was null on all of them.

`partner_id` is not seeded. **comms stamps it from the routing result** when a
call connects. Your calls never connected, so there was nothing to stamp. The
null was a symptom of the same thing as your `409 no attorney is available`, not
a separate data gap.

Two things changed:

1. **A real case now exists on the test member**
   (`munyira851@gmail.com`), shaped the way a completed call would leave it:

   ```
   jurisdiction: West (US region — the member is in California)
   partner:      Coastal Counsel LLP
   title:        Traffic Stop — consult with Coastal Counsel
   ```

2. **Coastal Counsel's seven attorneys now cover the member's region.** They
   previously covered only "Dev Test Jurisdiction", so a call placed from
   California routed to nobody. They now cover `West` and
   `United States (National)`, matching how routing widens its search.

**On `partnerAttorneys` returning `[]` for you** — that query lives in the
workforce subgraph and is permission-gated; a Member role cannot read it, by
design. For attorney pre-selection, tell us what the screen actually needs to
show and we will add a member-safe query rather than loosening that one. See the
question at the end.

**On the jurisdiction you hardcode** (`de400000-…-0001`): that is "Dev Test
Jurisdiction", a synthetic row in a country that is not the member's. It works,
but it routes to the wrong pool. Prefer the jurisdiction from the member's case,
or send `currentCountry` / `currentSubdivision` and let routing resolve it.

### A5 — a member can now delete their own document · shipped

You were right that this was the outlier. `requestUserDocumentUpload`,
`createUserDocument` and `userDocumentDownloadUrl` were all self-or-admin;
`deleteUserDocument` alone required the admin permission, which made the Glovebox
one-way.

`deleteUserDocument(id:)` now loads the row first and authorizes the caller
against **that document's owner**. A member deleting their own file succeeds; a
member reaching for someone else's still gets `forbidden`.

**You can ship the ✕ on every tile.** Your two stuck files (`probe.txt`,
`ui.xml`) are now yours to remove.

> Not shipping a control that always fails was the right call.

### A6 — the document-field `type` vocabulary · answered

Here is the honest answer: **`type` is a free-form string with no enforced
vocabulary**, which is why you found `example 3` next to `text`. Your rule —
render `text`, `dropdown`, `file`, treat everything else as not-member-input — is
the correct defensive read and I would keep it.

The intended set, and what each should render as:

| `type` | Render as | Member input? |
|---|---|---|
| `text` | single-line text field | yes |
| `dropdown` | picker, options from the field's option rows | yes |
| `file` | document upload | yes |
| `image` | **document upload, restricted to image MIME types** | yes |
| `agreement` / `policy` / `guide` / `form` | — | **no**, organisation templates |
| `example*` | — | **no**, dev leftovers |

**On `image`:** it *is* an upload, so your first instinct was right — but do not
change your mapping yet. The reason "Policy" appeared in the member's Glovebox is
that Policy has an `image` field called "Example", and that is a data problem, not
a type problem. Treating `image` as unknown is the safer position **until the
templates are cleaned up**, because mapping it today re-admits Policy.

I would rather fix the data than have you carry a workaround. Keeping `image` as
unknown for now; I will tell you when it is safe to map.

**Dev rows tidied:** `contract 2` and `Extra books` are now `is_active = 0`, so
`adminDocumentTypeList(activeOnly: true)` stops returning them. Deactivated
rather than deleted — `user_documents` may reference them, and a delete that
cascades through a member's uploaded files is not a tidy-up.

### A7 — `addSubaccount` now rejects an unknown `seatPriceID` · shipped

Good catch, and a good instinct to report it rather than route around it.

The price was only read further down, and only when a **paid** seat was actually
needed — so a nonsense id went unnoticed as long as the plan had an included slot
free, leaving a seat billing against nothing. It is validated on the way in now,
so a wrong id fails identically regardless of how many seats the plan includes.

### A8 — attorney names on the timeline · shipped as a new field

I did not fix the nested resolver, and I want to be straight about why.

`PartnerAttorney` in comms is a **federation reference stub** — comms owns only
its `id`. Selecting `attorney { displayName }` asks the gateway to resolve the
entity across subgraphs, and that hop hangs. It is the same merge problem that
422s the type at schema-merge time; making it work is a gateway change with real
blast radius, and it would still cost you a network hop per row.

comms already reads `display_name` locally for routing. So:

```graphql
attorneyAssignments {
  id
  status
  attorneyId
  attorneyDisplayName   # ← new: String, null when unknown
}
```

No federation, no extra query, same dataloader. **Use this instead of
`attorney { displayName }`** — the nested selection still exists for the desktop
app and still hangs.

**You can ship attorney names on the Activity timeline.**

---

## B. Operations that did not exist

### B1 — phone verification · shipped

```graphql
requestPhoneVerification(phoneE164: String!): RequestPhoneVerificationResult!
# → { sent, maskedPhone, expiresInSeconds }

verifyPhone(phoneE164: String!, code: String!): Boolean!
```

Both are self-scoped: the target comes from your access token, not an argument.
On success the number is stored on the account and `phoneVerifiedAt` is stamped.

You were right that `requestLoginOtp(channel: SMS)` is circular — it sends to the
number already on the account.

**Answering your code-length question: six digits here.** Sign-in codes stay at
four. Your design's six-cell entry describes this operation, so build for six on
screens 08/09 and keep four on sign-in.

Limits worth knowing: 5 sends per member per hour, 10-minute expiry, 5 wrong
tries burns the code, and each new send invalidates the previous one — so a
Resend makes the old code stop working. A wrong, expired and already-used code
all return the same error deliberately.

`phoneE164` must be genuine E.164 (`+14155550123`); `4155550123` is rejected.

### B2 — pronouns · shipped

`pronouns: String` on `UpdateMyProfileInput` and readable on `UserProfile`. Free
text, member-supplied, never derived from `gender`.

### B3 — situation preferences · shipped

```graphql
myCommonSituations: [ID!]!
setMyCommonSituations(incidentTypeIds: [ID!]!): [ID!]!
```

Roughly what you proposed, with three differences:

- The setter **returns the stored list**, so you render what the server kept
  rather than what you sent.
- Duplicates are collapsed rather than rejected — the same id twice is a client
  slip, not something a member can mean.
- Every id must be a real incident type. An unknown one is an error, because a
  silently-saved typo becomes a blank tile on Home with nothing to explain it.

An empty list clears the selection. **An empty result means "no choice saved" —
fall back to the full incident list, which is what Home does today.**

### B4 — emergency-contact notify-by · shipped

`notifyBySms` and `notifyByEmail` — two booleans, on the type and both inputs.

You were right not to put this in `notes`. Free text used as a settings column
works right up until something reads `notes` expecting notes.

**Both default to `false`,** and that is deliberate: nothing sends these alerts
yet (see C4), so defaulting them on would record a member's consent to contact a
third party that they never gave.

### B5 — trial and guest · question back to you

Not built, and I do not want to guess at it. You asked the question that decides
the design, and it is a product decision rather than a backend one:

> **is a guest a real account with a role, or purely local state?**

Your second point is sharper than the first and I want to make sure it is not
lost: `requestLoginOtp` **deliberately does not enumerate accounts**. An unknown
address returns `sent: true` with the address masked back. That is correct
security and it is not changing. So **the app cannot detect an unrecognised email
at sign-in**, and guest mode cannot be entered the way the design describes —
regardless of how the guest model resolves.

Worse: self-serve sign-up is enabled on dev, so an unknown email that verifies a
code **creates a real member account**. The design's "unrecognised email →
guest" branch would collide with that.

That branch needs redesigning with the product owner, not implementing. Flagged.

### B6 — member-readable transcript · not planned yet

Nothing matching `transcript` exists, and nothing is scheduled. `CommsCallRecording`
is recordings, and `biCallRecordingUrl` is a BI operation a member cannot call.

There *is* live transcription in the platform (the real-time subtitle pipeline
feeds Amazon Transcribe), but it is not persisted as a member-readable artifact.
Turning it into one is a real piece of work plus a retention/privacy decision.

**Do not wire the link.** Shipping the timeline without it was right. I will come
back to you if this gets scheduled.

### B7 — changing a card in-app · you already have what you need

Option (c), and the key is already public.

`stripePublishableKey` is a **tokenless** query on the finance subgraph — you can
read it without a token, the same way the web checkout does. So:

```graphql
query { stripePublishableKey }
```

Then use Stripe's native iOS/Android SDK to tokenise the card, and:

```graphql
attachPaymentMethod(providerRef: "<pm_… from the Stripe SDK>")
setDefaultPaymentMethod(id: …)
detachPaymentMethod(id: <the old one>)
```

Two things to set expectations on:

- **There is no `updatePaymentMethod`, and there should not be.** With Stripe you
  do not edit a card — you attach a new one, make it default, detach the old. The
  design's inline expiry edit is not a thing the provider supports; screen 33D
  should become "replace card".
- **Billing ZIP is genuinely absent** from `PaymentMethod`. Stripe holds it on
  the payment method, we do not mirror it. If you need to display it, say so and
  I will surface it; if you only need to *collect* it, the Stripe SDK takes it
  during tokenisation and you do not need us at all.

The web client uses shared Stripe Elements card fields for all four of its card
flows, so you are on the same path — nothing bespoke.

### B8 — notification categories, frequency, and `kind` · shipped

On `UpdateMyProfileInput` and readable on `UserProfile`:

```graphql
notifySetupReminders:  Boolean   # "Setup reminders"
notifyTips:            Boolean   # "Tips & know-your-rights"
notifyAccountBilling:  Boolean   # "Account & billing"
notificationFrequency: String    # occasionally | rarely | off
```

All three categories **default to `true`**, and `notificationFrequency` defaults
to `occasionally`, so a member who never opens screen 26 behaves exactly as they
do today. Anything other than those three frequency values is rejected.

"Safety-critical (always on)" has no field because it is not optional — there is
nothing to store, and `notificationFrequency` does not apply to it.

**You were right to refuse to map "Tips" onto `marketingOptIn`,** and I want to
say so explicitly rather than just quietly agreeing. It is a marketing-consent
record with legal weight. Showing it as "Marketing emails" is exactly right; it
stays what it is, and `notifyTips` is the content preference.

**On `kind`:** it is free-form and unvalidated — which is why
`"totally-made-up-kind"` was accepted. There is no intended vocabulary today.
Your approach (carry it through, group loosely, do not switch on it) is the right
one and I would keep it until we define one. Given what `type` cost you in A6, I
am not going to hand you a list I would have to change.

**On `createNotification` being member-callable:** you are right that it is odd.
It is correctly scoped (other users are refused), so it is not a hole, and I have
left it alone rather than break a caller I have not audited. Noted for a proper
look.

---

## C. Your eight questions, answered

**C1 — what is `countryISO2` on `verifyLoginOtp` for?**
It stamps the member's **home country** on their profile, but **only when they do
not already have one**. Home country drives products, currency and billing. The
"only when unset" is load-bearing: this runs on every verification, including an
existing member signing in from abroad, and overwriting would re-home a Kenyan
member who logged in from a London hotel.

**Send the device's real country.** It is how a self-serve member gets a home
country without being asked a question we can already answer. `null` is not
harmful, but it leaves the member's billing country unset until something else
fills it.

**C2 — access-token lifetime, and does refreshing rotate the refresh token?**

- Access token: **6 hours**.
- Refresh token: **30 days**.
- **Yes, refresh rotates.** Each refresh token is **single-use** — refreshing
  mints a new access token *and* a new refresh token, and the old one is spent.

This is the answer you were waiting on, so here is the trap that comes with it,
because the web client hit it hard:

> **Never fire two refreshes with the same token.** Opening the app after the
> access token expires fires a burst of parallel queries that all 401 at once. If
> each launches its own refresh, the first rotates the token, every other presents
> a spent one, gets told the session is gone, and signs the member out — even
> though the refresh token was good for another 30 days. That is what "it logs me
> out when I've been away" is.
>
> Funnel every refresh through **one shared in-flight promise**. This matters more
> for you than for the web: a backgrounded app wakes up into exactly that burst.

Also: there is a grace window for a session superseded by another device, so an
in-call device is not cut off mid-consultation.

**C3 — is `verifyMemberPin` the intended server-side gate for ending a call?**
Yes. The PIN's only job is ending a live session securely. It does not unlock the
app and does not protect recordings — your reading of the design is correct.

Worth knowing: the gate applies to **the member ending a live call**. The
attorney ending it is the deliberate un-gated escape hatch, so a member who
cannot produce their PIN is never trapped in a call.

**C4 — who sends the emergency-contact alert?**

**Nobody. It is not built.** I checked comms end to end: nothing references
emergency contacts, and there is no producer for that alert in any service.

The design promises contacts are "alerted with your location the moment you
connect to an attorney" and that promise is currently unkept by everyone. It
should be server-side — you only call `member-call`, and the client is the wrong
place to guarantee a safety-critical side effect.

**Do not wire anything to it, and do not show copy that promises it.** This is
now on our list; I have raised it as a product gap.

**C5 — is one-device-at-a-time deliberate and permanent?**
Deliberate, yes. Signing in anywhere supersedes the previous session — that is
why `LoginPayload` returns `otherSessionsRevoked` and `mySessionStatus` reports
`another_device`.

Your concern is legitimate and worth escalating, so I am recording it rather than
waving it off: for an app people open during a police encounter, signing in on a
laptop signing out the phone in their pocket is a real failure mode. There is
already a grace window so an **in-call** device is not cut off. Whether phones
should be exempt entirely is a product decision I have flagged.

**C6 — inconsistent casing (`userID` vs `userId` vs `memberUserId`).**
Real, and it is our mess: different services were generated at different times.
Following whatever each operation asks for is the only correct approach today.

I am not renaming existing fields — that breaks every client at once for
cosmetics. **New fields will use `camelCase` with a lowercase `d` (`userId`)**,
which is the majority convention. Everything I shipped today follows it.

**C7 — sign-in codes are 4 digits.**
Confirmed, and they stay 4. Phone verification (B1) is **6**, which is what your
six-cell design describes. Two different codes for two different jobs.

**C8 — an "onboarding complete" flag.**
Now exists, because you were right that a flag is more honest than an inference:

```graphql
completeMyOnboarding: UserProfile!      # mutation, idempotent
UserProfile.onboardingCompletedAt: String   # null until finished
```

Call it when the member finishes the wizard. Calling it again keeps the original
timestamp, so it stays a record of *when* rather than *that*. You can drop the
date-of-birth + address + PIN + password + contacts inference.

---

## E. Not the gateway

**E1 — deep-link contract: your implementation is the contract.**
`/app/return`, `/return-to-app` and `/app` on `attorney-shield.com` and
`www.attorney-shield.com`, carrying `email` and nothing else. No change needed.

And you were right to pre-empt this: **the link will never carry a credential.**
Treating it as untrusted input, with a test asserting that `accessToken`,
`userID` and `roles` yield nothing but the email, is exactly right. Keep that
test.

**E2 — domain verification files.** Forwarded to whoever owns web hosting. Send
the signing-certificate SHA-256 fingerprint and Team ID when your release keystore
exists and the files go up.

---

## Questions back to you

1. **D1 — when will your builds send `Authorization` on `/api/*`?** We hold dev
   in `warn` until then. No rush, just tell us.
2. **A4 / attorney pre-selection — what does the screen need to show?** Names
   only? Names plus photo, specialty, availability? `partnerAttorneys` is
   staff-only by design, so I would rather add a member-safe query shaped to the
   screen than widen that one.
3. **B5 — a guest is…?** And separately: given that `requestLoginOtp` cannot
   reveal an unknown email, how do you want the guest entry point to work? That
   branch needs redesigning either way.
4. **B7 — do you need to display the billing ZIP, or only collect it?** Collect
   is free (Stripe SDK). Display means we mirror a field we currently do not.

---

## Corrections to my own side of the ledger

Two things in your document that were reported as backend gaps but are not:

- **`member-call` returning `409 no attorney is available`** is correct
  behaviour, not a bug. It needs an attorney online in the desktop app. Your plan
  to run one yourselves is the right one — nothing to fix.
- **`partnerAttorneys` returning `[]`** is a permission boundary working as
  designed, not empty data. Seven active attorneys exist under the dev partner.

And one thing you did not report that I found while in there: the
`member-documents` endpoint was leaking members' identity documents to anyone
with a callId. Fixed in the same pass as D1. Your D1 report is what sent me
looking.
