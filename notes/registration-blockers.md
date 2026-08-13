# Registration — what is blocking us

**From:** mobile (Android + iOS)
**Date:** 2026-08-13
**Scope:** only the registration and profile-completion journey. Nothing else.

> A narrow subset of [backend-asks.md](backend-asks.md), kept for when only the
> registration blockers need sending. Both are current; do not edit one without
> the other.

**Built and writing to dev since the last version:** the profile checklist
(screen 13), "Set a password" (13A), and the emergency-contact form (16) minus
its notify-by control.

Everything below was checked against
`https://gateway-dev.attorneyshield.io/query` by introspecting the schema and
calling the operations as the test member — not inferred from the web client.

---

## Already working — no action needed

So you know what not to look at:

| Step | Operation |
|---|---|
| Sign in, password | `login` |
| Sign in, one-time code | `requestLoginOtp` / `verifyLoginOtp` |
| Date of birth, gender | `updateMyProfile` |
| Home address | `updateMyProfile` |
| Separate mailing address | `createUserAddress` |
| Security PIN | `setMemberPin` / `memberPinStatus` |
| Set a password | `setPassword` |
| Emergency contact — name, phone, email, relationship | `createEmergencyContact` |
| Whether a password exists, for the checklist | `User.hasPassword` |
| States/provinces | `subdivisionsByCountry` — all 50 US states resolve |

Those steps are **built and verified writing to dev.**

---

## The blockers

### 1. Phone verification — no operations exist

**Blocks design screens 08 and 09** ("Enter your phone number", "Verify your
phone").

- `updateMyContactInfo(input: { phoneE164 })` **stores** a number. That works.
- **Nothing sends or checks a phone code.** We searched all 297 mutations: no
  `requestPhoneOtp`, no `verifyPhone`, nothing equivalent.
- `requestLoginOtp(channel: SMS)` is a **sign-in** code sent to an
  *already-verified* phone. It cannot verify a new number — it is circular.
- `phoneVerifiedAt` is writable only through `CreateUserInput` /
  `UpdateUserInput`, which are admin operations, not member self-service.

**What we need:** two operations a signed-in member can call —

1. send a verification code to a supplied number, and
2. verify that code, setting `phoneVerifiedAt` on success.

**Also please confirm the code length.** Sign-in codes are 4 digits; the design
specifies 6 for phone verification. We would rather match you than guess.

> We have deliberately **not** shipped screen 08 on its own. Its sub-line
> promises "We'll text a code to verify it", and rewording that to hide the
> missing half would leave a feature that looks finished and never gets
> revisited.

---

### 2. Pronouns — no field exists

**Blocks the last field of design screen 10** ("A few personal details": date of
birth, gender, **pronouns**).

Date of birth and gender are both on `UpdateMyProfileInput`. Pronouns are not —
and there is no field named `pronoun*` on **any** input type in the schema, and no
type with `pronoun` in its name.

**What we need:** one nullable string on `UpdateMyProfileInput` (and, if you want
it readable, on `UserProfile`).

We left the input out rather than collect it and silently drop it.

---

### 3. Situation preferences — no operations exist

**Blocks design screens 13B, 13C** (and 27B later): the member's saved "three most
common situations", chosen from the incident types.

Nothing matching `situation`, `preference` or `favourite` in 238 queries or 297
mutations.

**What we need:** a read and a write, capped at three incident-type IDs per
member. Roughly:

```graphql
myCommonSituations: [ID!]!
setMyCommonSituations(incidentTypeIds: [ID!]!): Boolean
```

Home currently shows the full incident list because there is nowhere to store a
choice of three.

---

### 4. Emergency contacts have no "notify them by" preference

**Blocks two controls on design screen 16**, not the whole screen — the rest of
that form is built and writing to dev.

The design collects *how* each contact should be alerted: "Notify them by — Text
message / Email / Choose one or both".

`CreateEmergencyContactInput` has `userId`, `name`, `relationship`, `phoneE164`,
`email`, `isPrimary`, `notes`. **There is no notify-by field**, and nothing
matching `notify` exists on any input type in the schema.

We could have stuffed it into `notes`, but that is a free-text field being used
as a settings column — it would work until something reads `notes` expecting
notes.

**What we need:** either two booleans (`notifyBySms`, `notifyByEmail`) or a small
enum on the contact.

> Worth knowing regardless of the field: **who actually sends these alerts?** The
> design says contacts are "alerted with your location the moment you connect to
> an attorney". We only ever call `member-call`, so that alert must be sent
> server-side. If the app is expected to trigger it, we need an operation for it.

---

### 5. The Glovebox has endpoints but no data

**Blocks design screens 14, 14A, 14B, 14C, 14D** (Upload documents, and the
Driver's / Health / Gun / Citizenship sections).

This one is **seeding, not missing operations.** The operations are all there:

- `adminDocumentTypeList` — the sections
- `adminDocumentFieldList` — the fields inside each section
- `requestUserDocumentUpload(userId, adminDocumentFieldsId, fileName, contentType, sizeBytes)`
- `createUserDocument`, `userDocumentList`, `userDocumentDownloadUrl`
- `saveUserDocumentValue(userId, adminDocumentFieldsId, value)` for the plain
  text fields

But:

```
adminDocumentTypeList → []
```

Every upload and every saved value is keyed by **`adminDocumentFieldsId`**. With
no document types and therefore no fields, there is nothing to attach a document
or a value to. We cannot build any of the four sections until they exist.

**What we need on dev:** the four sections seeded with their fields, matching the
design —

| Section | Fields the design shows |
|---|---|
| Driver's Information | licence document upload |
| Health Information | three plain text fields + document upload |
| Gun Information | two yes/no questions, permit number, issue state |
| Citizenship Info | plain fields + document upload |

If the field types are configurable per organisation, we mainly need to know
**what `fieldType` values exist**, so we can render the right control for each.

---

### 6. Incident types are still empty

Not strictly registration, but it is the screen registration **lands on**, so
finishing onboarding currently ends at a home screen that says "No incident types
are configured yet."

```
adminIncidentTypeList(activeOnly: false)                      → []
adminIncidentTypeList(activeOnly: true, countryISO2: "US")     → []
adminLanguageList                                             → 1 entry, ar-SA, isDefault: false
```

Retested while authenticated, with and without a country filter, so this is not a
country-filter side-effect.

**What we need:** incident types seeded with translations (the design uses Traffic
Stop, Auto Accident, Pedestrian Stop, Domestic, Test Call, Other), plus an English
language entry marked `isDefault: true` — otherwise our label resolution falls
through to Arabic.

**Separately:** `countries` returns `[]`, while `country(id:)` resolves United
States and `subdivisionsByCountry` returns all 50 states on the same records. The
list query looks broken or scoped unintentionally. We read the country from the
member's profile instead, so it is not blocking us — but you should know.

---

## What we ship as each lands

| You give us | We ship |
|---|---|
| Phone send + verify operations (§1) | Screens 08 and 09 |
| A pronouns field (§2) | The last field of screen 10 |
| Situation preference read/write (§3) | Screens 13B, 13C, and the saved-three row on Home |
| A notify-by field on emergency contacts (§4) | The last two controls of screen 16 |
| Document types + fields seeded (§5) | Screens 14, 14A–14D — the whole Glovebox |
| Incident types + an English language (§6) | A home screen with real tiles, and a call with a real incident type |

Nothing here is worked around with a placeholder. Where a backend piece is
missing, the screen is **left unbuilt and listed above**, so it cannot be
forgotten.
