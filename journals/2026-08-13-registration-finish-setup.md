# 2026-08-13 — Registration screens 08–12 ("Finish setup")

## Task

Build the design reference's Stage 4, screens 08 through 12.

## Outcome

**Three of the five shipped. Two are not built, on purpose, and are on the
backend list.**

| Screen | Status |
|---|---|
| 08 — Enter phone number | **Not built** — see below |
| 09 — Verify phone | **Not built** — no endpoint exists |
| 10 — Personal details | Built, minus pronouns |
| 11 — Address | Built |
| 12 — Security PIN | Built |

So the wizard is "Step N of 3", not 5.

---

## What introspection settled before any code

| Question | Answer |
|---|---|
| Date format | **`YYYY-MM-DD` only.** The gateway replies `invalid dateOfBirth (expected YYYY-MM-DD)` |
| `Gender` enum | `male`, `female`, `other`, `non_binary`, `unspecified` — **lower-case**, unlike every other enum here |
| PIN | `setMemberPin(userId, pin)` → Boolean; `memberPinStatus { isSet }` |
| Address | `updateMyProfile` carries the address; `createUserAddress` adds labelled extras |
| Phone storage | `updateMyContactInfo(input: { phoneE164 })` — verified working |
| Phone *verification* | **Does not exist** |
| Pronouns | **Does not exist** anywhere |

Casing trap worth remembering: `updateMyProfile` takes `countryId`/`subdivisionId`
while `createUserProfile` takes `countryID`/`subdivisionID`.

---

## Why 08 and 09 are not built

This is the decision worth recording, because I got it wrong first.

I initially built screen 08 and changed its sub-line from the design's "We'll text
a code to verify it" to "So an attorney can reach you if a video call ever drops"
— because we cannot text a code. That reads fine. It is also exactly the failure
mode Samson flagged mid-task: *covering a backend gap with something that looks
finished, which nobody then comes back to.*

The facts:

- `updateMyContactInfo` stores a number. That half works.
- **Nothing in 297 mutations sends or checks a phone code.** No `requestPhoneOtp`,
  no `verifyPhone`. `requestLoginOtp(channel: SMS)` is a *sign-in* code to an
  already-verified phone, so it cannot verify a new number — it is circular.
- `phoneVerifiedAt` is writable only via admin `createUser`/`updateUser`.

So a member could enter a number and it would sit there unverified forever, with
the screen's own promise quietly rewritten to conceal it. I removed the step, the
API method, and all the phone plumbing, and put both screens on the backend list
with what is needed.

Same reasoning for **pronouns**: DOB and gender have fields, pronouns do not, so
the input is absent rather than collected and discarded.

---

## A correction I owe the backend

Earlier I told them **no countries were configured**. That was wrong.

| Query | Result |
|---|---|
| `countries` | `[]` |
| `country(id: f989d06a-…)` | **United States, `US`** |
| `subdivisionsByCountry(<that id>)` | **all 50 states + DC** |

The data is there. **The `countries` list query is what returns empty**, while
`country(id:)` and `subdivisionsByCountry` resolve the same records fine. The test
member's own profile points at that US id.

Incident types and languages *are* genuinely still empty — retested
authenticated, with and without a country filter.

I read the country from the member's profile rather than a picker, which is
arguably more correct anyway, but the list query is broken and the handoff now
says so instead of silently routing around it.

Second time I have been wrong about something existing by not asking the schema
directly. The lesson keeps being the same one.

---

## Files touched

**`kotlin`** — `Models.kt` (Gender, UserProfile, ProfilePatch, Subdivision),
`AsiApi.kt` (6 operations), `AsiComponents.kt` (`AsiStepHeader`, `AsiInfoChip`,
`AsiSelectField`, `AsiCheckboxRow`, `AsiPinPad`), `feature/setup/` (new),
`MainActivity.kt`, plus `SetupViewModelTest`, `AccessibilityTest`,
`DynamicTypeTest`.

**`swift`** — the same structure: `Models.swift`, `AsiApi.swift`,
`AsiComponents.swift`, `Feature/Setup/`, `AttorneyShieldApp.swift`,
`SetupViewModelTests`.

---

## Decisions

**Every step is skippable.** The reference has no skip. This is an app people open
during a police encounter, and standing between someone and an attorney to collect
a postcode is the wrong trade, so "Finish later" goes straight to Home from any
step. Worth a product ruling.

**The wizard only runs after a fresh sign-in**, never on a restored session, so
nobody is nagged on every cold start.

**A failed lookup never forces the wizard on.** If `memberPinStatus` errors we
assume the PIN is set. Treating "unknown" as "missing" would trap a finished
member in setup every time the network hiccuped.

**Each step saves as the member leaves it** rather than batching to the end, so a
failure costs one step instead of three.

**A state picker was added to screen 11**, which the design does not have. The
profile carries `subdivisionId`, the screen's own info chip promises "your home
jurisdiction", and a US address with no state is incomplete — jurisdiction cannot
be derived from a ZIP on the device. Shown only when the list resolves, so an
environment without subdivisions is not blocked by it.

**The mailing-address checkbox reveals a second address block** when unchecked,
written via `createUserAddress(label: "Mailing", isDefault: false)`. The design
shows the checkbox but no second form; a checkbox that does nothing seemed worse.

**A custom PIN keypad rather than the system keyboard.** The reference specifies
it, and for a PIN it is also better: no keyboard covering the screen, no paste, no
third-party IME in the path.

**The PIN does not auto-submit** on the fourth digit, unlike the sign-in code. A
PIN is worth a deliberate confirmation; a sign-in code only the server can judge.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **175 pass**, 0 fail (was 154) |
| Android instrumented | **28 pass**, 0 fail (was 24) |
| iOS unit | **175 pass**, 0 fail (was 154) |

Coverage includes the ISO date conversion, 31 February and future dates rejected,
leap years, step gating, the state requirement degrading when the list is empty,
ISO + lower-case gender actually on the wire, the mailing address written only
when different, the PIN confirm/mismatch path, the setup gate skipping a complete
member, a failed PIN lookup not forcing the wizard, prefill, and the PIN pad at 2×
font scale and under TalkBack.

### Verified end to end on device, against gateway-dev

Signed in on the simulator as the test member and walked all three steps. Read
back from the server afterwards:

```json
{"dateOfBirth": "1990-05-14", "addressLine1": "123 Main St",
 "city": "Springfield", "postalCode": "62701",
 "subdivision": {"code": "CA", "name": "California"},
 "memberPinStatus": {"isSet": false}}
```

- The DOB wrote as ISO from an MM/DD/YYYY form
- The **state picker listed all 50 real states** from `subdivisionsByCountry`,
  alphabetically, and wrote a real subdivision id
- `isSet: false` confirms the PIN mismatch guard never reached the gateway
- A restored session went straight to Home, skipping the gate, as designed

---

## A bug found only by tapping through it

On the PIN confirm step, entering a mismatched PIN showed the error banner — and
then **the first keypress of the retry cleared the banner, which moved the whole
keypad up mid-entry**, so the next digit landed on whatever key slid under the
finger. I hit it myself while driving the simulator and produced a second
"mismatch" that was really a mis-tap.

Fixed by not clearing the error while typing a PIN; it clears on the next submit,
so the keypad never moves while in use. Regression-tested on both platforms.

Every unit test passed throughout. It was only visible on a device — same as the
code-field focus bug yesterday and the clipped carousel tile before that.

---

## Open issues / next steps

1. **Screens 08 and 09 need backend work** — an operation to send a code to a new
   number and one to verify it, setting `phoneVerifiedAt`. Also confirm the code
   length: sign-in is 4 digits, the design says 6 for phone.
2. **Pronouns needs one nullable field** on `UpdateMyProfileInput`.
3. **`countries` returns empty** while the rows resolve by id.
4. **Nobody has ruled on an age gate.** DOB is collected and validated as a real
   past date, but nothing checks 18+. If membership has a minimum age that is a
   product decision, not a technical one.
5. **`gender` is stored but never displayed** anywhere in the app yet.
6. Setup completeness is judged from DOB + address + PIN. If the backend gains a
   real "onboarding complete" flag we should use that instead of inferring.
