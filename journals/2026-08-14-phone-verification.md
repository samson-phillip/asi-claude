# 2026-08-14 — Screens 08 and 09: phone entry and verification

## Task

Build the two setup screens that were held back: **08** (enter your phone
number) and **09** (verify it with a texted code). Both platforms.

These were the only screens deliberately *not* built when Stage 4 went in. The
design promises "We'll text a code to verify it", and until this week nothing in
the schema could send or check one — `phoneVerifiedAt` was writable only by the
admin `updateUser`. Shipping screen 08 alone would have meant rewording the
design's own promise to hide the missing half, so both went on the backend list
instead (A2/A3 in `notes/backend-asks.md`).

The backend's round-2 reply says they landed. This closes them.

## Repos and files touched

### `kotlin`
| File | What |
|---|---|
| `core/format/PhoneNumber.kt` | **New.** E.164 assembly and display formatting. |
| `core/network/AsiApi.kt` | `requestPhoneVerification`, `verifyPhone`; `getMe` now selects `phoneVerifiedAt`. |
| `core/network/Models.kt` | `PhoneVerificationRequest` + wire types; `Me.phoneVerifiedAt`. |
| `feature/setup/SetupViewModel.kt` | Two new steps, the skip rule, the resend countdown. |
| `feature/setup/SetupScreen.kt` | `PhonePane`, `VerifyPhonePane`. |
| `MainActivity.kt` | New callbacks wired. |
| `core/format/PhoneNumberTest.kt`, `feature/setup/SetupViewModelTest.kt` | Tests. |

### `swift`
Same shape: `Core/Format/PhoneNumber.swift` (new), `Core/Network/AsiApi.swift`,
`Core/Network/Models.swift`, `Feature/Setup/SetupViewModel.swift`,
`Feature/Setup/SetupScreen.swift`, `Core/Design/AsiComponents.swift`
(`AsiCodeField` gained an `accessibilityName`), plus
`AttorneyShieldTests/PhoneNumberTests.swift` (new) and additions to
`SetupViewModelTests.swift`.

### `asi-claude`
`notes/backend-asks.md` — A2 and A3 marked shipped and built.

## API endpoints used

Both on the GraphQL gateway, both self-scoped — the account comes from the
token, so neither can touch anyone else's number.

```graphql
mutation RequestPhoneVerification($phone: String!) {
  requestPhoneVerification(phoneE164: $phone) { sent maskedPhone expiresInSeconds }
}

mutation VerifyPhone($phone: String!, $code: String!) {
  verifyPhone(phoneE164: $phone, code: $code)
}
```

`user(id:)` now also selects `phoneVerifiedAt`, which is how the wizard knows
whether to show these two screens at all.

Read off the live schema rather than assumed:

- The code is **six digits**. Sign-in codes are four. Two different codes for
  two different jobs — the design's six-cell entry is this one, and building it
  as four would have made every real code unenterable.
- `expiresInSeconds` is **600** on dev.
- Sends are rate-limited to **five an hour**, and five wrong tries burn a code.
- A new send **invalidates the previous code**. The screen says so, because it
  is surprising: an older SMS silently stops working.
- Wrong, expired and already-used all return the **same** error string. That is
  deliberate, so the screen cannot tell a member which happened and must not
  pretend to.

**`requestPhoneVerification` was never called as a probe.** It sends a real SMS
and spends one of five an hour. Everything above came from introspection and
from the backend's own note; the operation itself is exercised only against
stubs. Live verification needs a phone number the user controls — see Open
issues.

## Decisions

### E.164 is refused, not guessed

`PhoneNumber.toE164` returns null rather than a best effort. The gateway wants
`+14155550123` and rejects `4155550123`, and a malformed number costs a member
an SMS they never receive *and* one of their five sends. When we cannot build a
number confidently — too short, too long, no dialling code, letters — the
Continue button simply stays off.

A leading zero is dropped: it is a national trunk prefix and never part of the
international form. `+44 07700 900123` is not a number.

Display formatting is `+1` only. Imposing US grouping on a foreign number would
make a member's own number look wrong to them, and an over-long `+1` number is
shown unformatted rather than truncated — never lose a digit the member typed.

### A verified member never sees these screens

`load()` reads `phoneVerifiedAt` and, when it is set, drops both steps from the
wizard: the header reads "Step 1 of 3", not "3 of 5". Asking someone to
re-verify a number they have already confirmed is a step they cannot pass for a
reason they cannot see, and it would spend an SMS to do it.

The navigation had to change with it. `back()` and the next-step computation now
walk the **filtered** list rather than the enum's declaration order, otherwise
Back from Details would land on a step this member never saw.

**An unreadable phone state counts as verified.** Same rule the PIN read already
follows: a network hiccup must not force someone back through a step they
completed.

### The code does not verify itself

Sign-in submits automatically on the last digit. This does not. Five wrong tries
burn the code and there are only five sends an hour, so a stray paste costing a
member their code — possibly their last send — is a worse trade than one extra
tap. Non-digits are still stripped rather than rejected, so pasting "Your code is
812345" straight from the notification works.

### Verification uses the number we texted

Not whatever is in the field. A member who edits the box after the code goes out
must not verify against a number nobody texted. The view-model keeps `phoneE164`
from the send and verifies against that.

### A countdown, not a dead button

While the code is live, resend is replaced by "You can ask for another code in
Ns" rather than a disabled button with no explanation. It also stops a member
burning their hourly allowance on taps.

## Two bugs the device found and the tests did not

Both are the same mistake made twice — formatting a field's *value* while the
member is typing — and both needed a real caret to show up.

**Android: the digits came out transposed.** Typing "415" put `(451` on screen.
The brackets lengthen the string without moving the caret, so each new digit
lands mid-number. Fixed with a `VisualTransformation`: the state stays raw
digits, only the rendering changes, and an `OffsetMapping` keeps the caret on
the digit the member is actually on. `PhoneVisualTransformationTest` pins the
mapping in both directions.

**iOS: nothing formatted at all, and then it ate keystrokes.** The field was
bound to a computed `Binding` — getter formats, setter stores digits. SwiftUI's
`TextField` does not re-read a binding it has just written through, so the
member saw `4155550123` while the model believed it was formatting. Rebinding
directly and reshaping in `onChange` fixed the display but swallowed input:
typing "415" left `(4`, because writing to the bound value mid-edit discards the
keystrokes already in flight. The write is now deferred by one turn and only
applies if the digits have not moved on since.

The lesson is worth keeping: a text field's formatting cannot be verified from a
view-model test. Neither platform's unit suite could have caught either of these.

## Verified on device

Both wizards open on **"Step 1 of 5 · Finish setup"** for the test account, whose
`phoneVerifiedAt` is null. Heading, promise, info chip, the split Code/Mobile
fields and a disabled Send code all match the design; the number formats to
`(415) 555-0123` and Send code turns gold.

**Send code was never tapped, on either platform.** `+14155550123` may well be
someone's number, and the mutation texts it.

## Test results

**Android — 368 tests, 0 failures.** New: 8 in `PhoneNumberTest`, 5 in
`PhoneVisualTransformationTest`, 11 in `SetupViewModelTest`.

Two Android tests are worth noting because the first attempt got them wrong:
`advanceUntilIdle()` drains the ten-minute countdown, leaving nothing to observe.
The blocked-resend case uses `advanceTimeBy(1_500)` to sit mid-countdown; the
elapsed case uses `advanceUntilIdle()` deliberately.

**iOS — 346 tests, 0 failures.** The Swift countdown uses real `Task.sleep`, so
the elapsed case is driven by a response with `expiresInSeconds: 0` — which is
the state the screen is in once a countdown has run out — rather than by waiting
ten minutes in a test.

The three `DynamicTypeUITests` failures in the same run are the pre-existing ones
recorded on 2026-08-13: they assume a signed-out simulator and fail whenever a
session is stored. Not from this work, and still worth fixing.

**One real inversion, caught by its own test.** The first iOS draft read the
phone state as `(try? await api.getMe(...))?.phoneVerifiedAt != nil`, which
collapses a failed read and a genuinely unverified number into the same `false` —
the exact opposite of the rule above. An explicit `do`/`catch` now.

Every pre-existing setup test needed a `phoneVerifiedAt` stub added, since
`load()` now makes a fourth call. They all describe an account that starts at
"your details", so they say the phone is verified.

## Open issues / next steps

- **Live verification is not done.** It needs a real phone number the user
  controls; `requestPhoneVerification` sends an actual SMS and there are five an
  hour. Screens verified on emulator and simulator for layout, state and the
  skip rule; the two mutations themselves are stub-tested only.
- Still queued: **B8** (the rest of screen 26), **B2** (pronouns, screen 10),
  **B4** (notify-by, screen 16), **C8** (`completeMyOnboarding`), **C2** (token
  refresh through one shared in-flight promise).
- Trial screens **V2, T5–T8** remain unverifiable — no known password for
  `tester6@ainnop.com`.
- With David: emergency-contact alert, guest model, specialty ordering.
