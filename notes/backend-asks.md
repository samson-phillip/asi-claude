# Attorney Shield 2.0 — Backend asks from the native apps

**From:** mobile (Android + iOS)
**Date:** 2026-08-13
**Environment:** `https://gateway-dev.attorneyshield.io/query` · `https://comms-dev.attorneyshield.io`

Every item below is something **you can act on**. Our own to-dos, design
questions and the things we are arranging ourselves are deliberately not here.

Everything was verified by introspecting the schema and calling the operations as
the test member — not inferred from the web client. Where we were wrong earlier,
it is corrected and marked.

---

## At a glance

| # | Ask | Severity | Unblocks |
|---|---|---|---|
| A1 | `countries` returns `[]` while the rows resolve by id | HIGH | Country/state pickers everywhere |
| A2 | Incident types not seeded (+ an English default language) | **BLOCKING** | The home screen and the whole call flow |
| A3 | Document types + fields not seeded | HIGH | The Glovebox — 5 screens |
| A4 | No case for the test member | MEDIUM | Attorney pre-selection, real jurisdiction |
| B1 | No phone send/verify operations | HIGH | Registration screens 08, 09 |
| B2 | No pronouns field | LOW | The last field of screen 10 |
| B3 | No situation-preference operations | HIGH | Screens 13B, 13C + the saved-three row on Home |
| B4 | No notify-by field on emergency contacts | MEDIUM | Two controls on screen 16 |
| B5 | No trial or guest operations | HIGH | 13 screens (V1–V2, T1–T8, G1–G3) |
| C1–C8 | Eight answers we are currently guessing | MEDIUM | Token refresh, PIN gate, guest design |
| D1 | `member-call` takes no authentication | **SECURITY** | — |
| E1–E2 | Deep-link contract + domain files (**not the gateway**) | HIGH | Silent web→app handoff |

---

## Already working — please don't re-do these

| Area | Operations |
|---|---|
| Sign in, password | `login` |
| Sign in, one-time code | `requestLoginOtp` / `verifyLoginOtp` |
| Date of birth, gender | `updateMyProfile` |
| Home + mailing address | `updateMyProfile`, `createUserAddress` |
| Security PIN | `setMemberPin`, `memberPinStatus` |
| Set a password | `setPassword`, `User.hasPassword` |
| Emergency contacts | `createEmergencyContact` + CRUD |
| States/provinces | `subdivisionsByCountry` — all 50 US states resolve |
| Video call credentials | `POST /api/vonage/video/member-call` |

All of the above are **built and writing to dev.** The Vonage SDK is also proven
on a real Android device: the native library loads, reports 2.32.1, and completes
a round trip to Vonage.

---

# A. Environment and seeding

### A1 — `countries` returns empty while the same rows resolve by id · HIGH

**Correction to what we told you earlier.** We previously said no countries were
configured. That was wrong:

| Query | Result |
|---|---|
| `countries { iso2 }` | `[]` |
| `country(id: "f989d06a-8813-11f1-a446-06cf81ac74a7")` | **United States, `US`** ✅ |
| `subdivisionsByCountry(<that id>)` | **all 50 states + DC** ✅ |

The data exists. The **list query** is what comes back empty, and our test
member's own profile points at that same US id.

We work around it by reading the country from the member's profile instead of
offering a picker — so it is not blocking us — but the list query looks broken or
scoped in a way nobody intended, and we would rather tell you than quietly route
around it.

### A2 — Incident types are not seeded · BLOCKING

```
adminIncidentTypeList(activeOnly: false)                    → []
adminIncidentTypeList(activeOnly: true, countryISO2: "US")   → []
adminLanguageList                                           → 1 entry: ar-SA, isDefault: false
```

Retested **while authenticated**, with and without a country filter, so this is
not a side-effect of A1.

**This is the one that hurts most.** The home screen shows "No incident types are
configured yet.", so we cannot exercise the incident tiles, the attorney chip row,
or place a call with a real incident type. Finishing onboarding currently lands the
member on an empty screen.

**Need:** incident types seeded with translations — the design uses Traffic Stop,
Auto Accident, Pedestrian Stop, Domestic, Test Call, Other — plus **an English
language entry marked `isDefault: true`**. Without the language, our label
resolution (English → org default → first available → humanized code) falls
through to Arabic.

### A3 — Document types and fields are not seeded · HIGH

```
adminDocumentTypeList → []
```

**The operations all exist** — `adminDocumentFieldList`,
`requestUserDocumentUpload`, `createUserDocument`, `userDocumentList`,
`userDocumentDownloadUrl`, and `saveUserDocumentValue` for plain text fields. So
this is a **seeding** ask, not a build ask.

Every upload and every saved value is keyed by **`adminDocumentFieldsId`**. With
no types there are no fields, so there is nothing to attach a document or a value
to, and none of the Glovebox can be built.

**Need:** the four sections seeded with their fields, per the design:

| Section | Fields the design shows |
|---|---|
| Driver's Information | licence document upload |
| Health Information | three plain text fields + document upload |
| Gun Information | two yes/no questions, permit number, issue state |
| Citizenship Info | plain fields + document upload |

Also please tell us **what `fieldType` values exist**, so we render the right
control for each field rather than guessing.

### A4 — No case for the test member · MEDIUM

`casesByUser(userID: <test member>)` → `[]`.

The member's organization resolves correctly
(`6c53e00d-8682-11f1-a446-06cf81ac74a7`), but with no case, jurisdiction and
partner fall back to the hard-coded dev seed ids and we cannot exercise attorney
pre-selection at all.

> If it is easier to point us at an environment that already has A1–A4, that
> works just as well. We only need somewhere to develop against.

---

# B. Operations that do not exist

We searched all **238 queries and 297 mutations** for each of these. Where a
backend piece is missing, we have **left the screen unbuilt and listed it here**
rather than shipping a placeholder that looks finished.

### B1 — Phone verification · HIGH · blocks screens 08, 09

- `updateMyContactInfo(input: { phoneE164 })` **stores** a number. That works.
- **Nothing sends or checks a phone code.** No `requestPhoneOtp`, no
  `verifyPhone`, nothing equivalent.
- `requestLoginOtp(channel: SMS)` is a **sign-in** code sent to an
  *already-verified* phone, so it cannot verify a new number — it is circular.
- `phoneVerifiedAt` is writable only via `CreateUserInput` / `UpdateUserInput`,
  which are admin operations, not member self-service.

**Need:** two operations a signed-in member can call — send a code to a supplied
number, and verify that code, setting `phoneVerifiedAt` on success.

**Also confirm the code length.** Sign-in codes are 4 digits; the design specifies
6 for phone verification.

> We deliberately did **not** ship screen 08 alone. Its own sub-line promises
> "We'll text a code to verify it", and rewording that to hide the missing half
> would leave a feature that looks finished and never gets revisited.

### B2 — Pronouns · LOW · blocks one field of screen 10

Date of birth and gender are both on `UpdateMyProfileInput`. Pronouns are not, and
no input type in the schema has a field matching `pronoun`.

**Need:** one nullable string on `UpdateMyProfileInput` (and on `UserProfile` if
you want it readable).

### B3 — Situation preferences · HIGH · blocks screens 13B, 13C, 27B

The member's saved "three most common situations". Nothing matching `situation`,
`preference` or `favourite` anywhere.

**Need:** a read and a write, capped at three incident-type IDs per member.
Roughly:

```graphql
myCommonSituations: [ID!]!
setMyCommonSituations(incidentTypeIds: [ID!]!): Boolean
```

Home currently shows the full incident list because there is nowhere to store a
choice of three.

### B4 — Emergency-contact notify-by · MEDIUM · blocks two controls on screen 16

The design collects *how* each contact is alerted: "Notify them by — Text message
/ Email / Choose one or both".

`CreateEmergencyContactInput` has `userId`, `name`, `relationship`, `phoneE164`,
`email`, `isPrimary`, `notes`. There is **no notify-by field**, and nothing
matching `notify` on any input type.

We could have written it into `notes`, but that is free text being used as a
settings column — it works until something reads `notes` expecting notes.

**Need:** two booleans (`notifyBySms`, `notifyByEmail`) or a small enum on the
contact.

### B5 — Trial and guest · HIGH · blocks 13 screens

Nothing matching `trial` or `guest`.

The design has a 7-day limited trial with an in-app conversion gate (V1–V2,
T1–T8) and a guest mode entered from an unrecognised email at sign-in (G1–G3).

**The question that decides the whole design: is a guest a real account with a
role, or purely local state?**

Note also that `requestLoginOtp` **deliberately does not enumerate accounts** — an
address with no account still returns `sent: true` with the submitted address
masked back. That is good security, and it means **the app cannot detect an
unrecognised email at sign-in**, so guest mode cannot be entered the way the
design describes. Whatever the model turns out to be, that branch needs
rethinking with you.

---

# C. Answers we need — each of these is a guess today

1. **`countryISO2` on `verifyLoginOtp`** — we send `null`, because it is optional
   and that is what the web client sends. But what is it *for*? If it affects
   routing or jurisdiction we would rather send something real.
2. **`refreshToken` — access-token lifetime, and does refreshing rotate the
   refresh token?** This matters more for us than for web: a browser tab is
   short-lived, but a native app sits backgrounded for days, and this is an app
   people open during a police encounter. **We have not wired refresh yet because
   of this.**
3. **Is `verifyMemberPin` the intended server-side gate for ending a call?** The
   design says the PIN's only job is ending a live session securely — it does not
   unlock the app or protect recordings.
4. **Who sends the emergency-contact alert?** The design says contacts are
   "alerted with your location the moment you connect to an attorney". We only
   ever call `member-call`, so it must be server-side — but if the app is meant to
   trigger it, we need an operation.
5. **Is one-device-at-a-time deliberate and permanent?** `LoginPayload` returns
   `otherSessionsRevoked` and `mySessionStatus` reports `another_device`, so
   signing in on the web ends the app's session and vice versa. We can live with
   it; it is worth confirming for a phone people open during an encounter, since
   signing in on a laptop signs out the phone in their pocket.
6. **Casing is inconsistent and we follow whatever each operation asks for** — the
   gateway mixes `userID` (`login`, `casesByUser`) with `userId` (`setMemberPin`,
   `updateMyProfile`'s `countryId`), and comms REST uses `memberUserId`. Worth
   settling before anyone adds a field.
7. **Sign-in codes are 4 digits** — confirmed live, and we have built for 4.
   Flagging only because the design specifies six-cell entry; we assume that
   describes phone verification (B1), which is a different code.
8. **Is there, or could there be, an "onboarding complete" flag?** We currently
   infer completeness from date of birth + address + PIN + password + contacts. A
   real flag would be more honest than our inference.

---

# D. Security

### D1 — `POST /api/vonage/video/member-call` takes no authentication

Anyone can place a call against any `organizationId` / `memberUserId` they can
guess, and that call routes to a **real attorney**.

Nothing we have built depends on it staying open, and we are not designing around
it. Flagging rather than assuming it is known.

---

# E. Not the gateway — please forward these

Both are blocking us, but neither is a backend/GraphQL task. Included so they do
not fall between teams.

### E1 — Deep-link contract for the web→app handoff · HIGH

Screens 07 and T4 hand the member back to the app "with email pre-filled", but
nothing records the actual path or parameter names.

**Currently implemented:** we accept `/app/return`, `/return-to-app` and `/app` on
`attorney-shield.com` and `www.attorney-shield.com`, reading an `email` query
parameter. It is confined to one file, so a confirmed contract is a one-line
change.

**Please do not design the link to carry a credential.** We treat it as untrusted
input — anyone can send a link. The email is a text-field prefill only, and we
have a test asserting that a link carrying `accessToken`, `userID` or `roles`
yields nothing but the email.

### E2 — Domain verification files · HIGH · web hosting

For a link to open the app *silently*, both hosts need:

- **Android:** `/.well-known/assetlinks.json` with our signing-certificate
  SHA-256 fingerprint for `com.app.attorney.shield`
- **iOS:** `/.well-known/apple-app-site-association` for our Team ID +
  `com.app.attorney.shield`

Until these exist, Android shows a "which app?" chooser and iOS universal links do
not fire at all. **We owe you the fingerprint and Team ID** once our release
keystore exists — that part is on us.

---

## What we ship as each lands

| You give us | We ship |
|---|---|
| A2 — incident types + an English language | A working home screen and a call with a real incident type |
| A3 — document types + fields | The Glovebox: screens 14, 14A–14D |
| A1, A4 — countries list, a test case | Real jurisdiction and attorney pre-selection |
| B1 — phone send/verify | Registration screens 08 and 09 |
| B2 — a pronouns field | The last field of screen 10 |
| B3 — situation preferences | Screens 13B, 13C and the saved-three row on Home |
| B4 — notify-by | The last two controls of screen 16 |
| B5 — a decision on the guest model | Trial and guest scoped, 13 screens |
| C2 — token lifetime and rotation | Token refresh, so sessions survive being backgrounded |
| C1, C3–C8 — the remaining answers | Guesses removed from code we have already shipped |
| E1 — the deep-link contract | A one-line change, then verified end to end |

---

## Where we are

Built and verified against dev: the welcome carousel, sign-in by password **and
one-time code**, the profile checklist, personal details, address, security PIN,
set-a-password, emergency contacts, the home screen, the call flow up to
"connecting", and the deep-link handler.

**One thing we have never been able to prove:** a video call actually going live.
`member-call` returns `409 no attorney is available` on dev. We are arranging an
attorney ourselves by running the desktop app — not an ask — but until that
happens, the step from "connecting" to a live picture is the one part of the
product still taken on faith.
