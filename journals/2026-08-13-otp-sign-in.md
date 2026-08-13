# 2026-08-13 — One-time-code sign-in

## Task

Build the OTP sign-in flow on both apps.

## Goal

Make a one-time code the **primary** way into the app, with the password as the
alternative — matching the reference client, where a code is the default login
method.

---

## What I did before writing any code

Phase 3 was previously blocked on six "shapes we would rather confirm than
guess". Three of them were about OTP. Rather than guess or wait, I asked the
gateway and read the deployed client's own bundle.

### Answered by introspection

| Question | Answer |
|---|---|
| `OtpChannel` values | `EMAIL`, `SMS` — nothing else |
| Does `verifyLoginOtp` return the same shape as `login`? | Yes — both return `LoginPayload` |
| Is `countryISO2` required? | **No.** Nullable, and the web client sends `null` when it does not know it |

`requestLoginOtp` returns a `RequestOtpResult` richer than expected:
`sent`, `channel`, `maskedEmail`, `maskedPhone`, `expiresInSeconds`. That is
enough to label where a code went, gate the SMS option on whether a phone is
verified, and drive a real resend countdown. `expiresInSeconds` is **300** on
dev.

### Answered by reading the deployed client's JS bundle

The exact operations, lifted verbatim so we cannot drift from the working
implementation:

```graphql
mutation RequestOtp($email: String!, $channel: OtpChannel!) {
  requestLoginOtp(email: $email, channel: $channel) {
    sent channel maskedEmail maskedPhone expiresInSeconds
  }
}

mutation VerifyOtp($email: String!, $code: String!, $country: String) {
  verifyLoginOtp(email: $email, code: $code, countryISO2: $country) {
    accessToken refreshToken userID roles otherSessionsRevoked
  }
}
```

The bundle also settled the interaction design: a **4-cell** entry that submits
automatically on the fourth digit, a `mm:ss` resend countdown, a channel switch
shown only when a phone exists, and a "use password instead" escape hatch.

---

## Three findings that changed the design

### 1. The code is 4 digits, not 6

The design reference shows a **six**-cell entry (screen 09) and calls it a
"6-digit SMS code". That screen is *registration phone verification* — a
different code from a different flow. Sign-in codes are 4 digits: the deployed
client renders four boxes and submits on the fourth.

Followed the live system, since `member-client` is the behavioural authority.
The length is one constant (`CODE_LENGTH` / `codeLength`) so it is a one-line
change if this is wrong.

### 2. The gateway deliberately does not enumerate accounts

An address that certainly has no account still returns:

```json
{"sent": true, "channel": "EMAIL", "maskedEmail": "de***@example.com",
 "maskedPhone": null, "expiresInSeconds": 300}
```

`maskedEmail` is just the submitted address masked back — **not** evidence an
account was found. This is good security behaviour, and it constrains us:

- No copy may imply we recognised the member. The confirmation line says where a
  code was sent, never that an account exists.
- **The design's guest-mode branch cannot key off this response.** Screens
  G1–G3 enter guest mode from "an unrecognised email at sign-in", and the
  sign-in endpoint will not tell us that. Whatever the guest model turns out to
  be, it cannot be detected here.

Pinned as a test on both platforms so nobody later "fixes" it into a leak.

### 3. Only one device can be signed in at a time

`LoginPayload` carries `otherSessionsRevoked`, the reference client states the
rule in its own sign-in footer, and there is a `mySessionStatus { status reason }`
query with an `another_device` reason.

So signing in on the web silently kills the app's session. Ours surfaces that as
"Your session has expired. Please sign in again." with no explanation of why —
see open concerns.

---

## Files touched

### `kotlin`
- `core/network/Models.kt` — `OtpChannel`, `OtpRequest`, wire types,
  `otherSessionsRevoked` on `LoginResult`
- `core/network/AsiApi.kt` — `requestLoginOtp`, `verifyLoginOtp`, `authed` flag
- `core/session/SessionManager.kt` — `signInWithOtp`, shared `adopt(...)`
- `core/design/AsiComponents.kt` — `AsiCodeField`
- `feature/auth/LoginViewModel.kt` — three-step machine, countdown
- `feature/auth/LoginScreen.kt` — email / code / password panes
- `MainActivity.kt` — wiring
- tests: `AsiApiTest`, `LoginViewModelTest`, `AccessibilityTest`, `DynamicTypeTest`

### `swift`
Same structure: `Models.swift`, `AsiApi.swift`, `SessionManager.swift`,
`AsiComponents.swift` (`AsiCodeField`), `LoginViewModel.swift`,
`LoginScreen.swift`, `AsiApiTests`, `LoginViewModelTests`.

---

## Decisions

**A code is the default, a password is the alternative.** Matches the reference.
The email survives crossing between panes — retyping an address to switch method
is exactly the friction that sends someone back to the web app.

**The sign-in operations no longer send a bearer token.** A member whose session
has just expired lands on the login screen still holding the dead token.
Attaching it turned the gateway's 401 into "Your session has expired" — locking
them out of the screen that fixes it. `login`, `requestLoginOtp` and
`verifyLoginOtp` now go out unauthenticated, with a regression test on both
platforms. This matters more now that a sign-in elsewhere revokes this session.

**One text field wearing boxes**, not four fields. The platform then handles
paste, backspace, IME and — on iOS, via `.oneTimeCode` — the keyboard's own
"From Messages" autofill. A screen reader announces one control
("Sign-in code, 2 of 4 digits entered") rather than four unlabelled cells.

**A rejected code clears the field.** All four boxes are full at that point, so
leaving it would make the member delete it before they could retry.

**Non-digits are dropped rather than rejected**, so pasting "1234" or even
"Your code is 1234" works.

**Both sign-in paths share one `adopt(...)`**, so password and code sign-in
cannot drift into resolving a member's context differently.

---

## API endpoints used

- `requestLoginOtp(email:, channel:)` → `RequestOtpResult` — unauthenticated
- `verifyLoginOtp(email:, code:, countryISO2:)` → `LoginPayload` — unauthenticated
- `login(input:)` — now also unauthenticated, and now selects `otherSessionsRevoked`

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **154 pass**, 0 fail (was 129) |
| Android instrumented | **24 pass**, 0 fail (was 20) |
| iOS unit | **154 pass**, 0 fail (was 129) |

New coverage: channel/enum mapping, no-enumeration behaviour, null country,
stale-token guard, auto-verify on the last digit, code clearing on rejection,
the countdown, channel switching, pane transitions preserving the email, the
4-cell layout at 2× font scale, single-control screen-reader announcement, and
focus-on-arrival.

### Verified on device against the live dev gateway

Drove both apps to the code pane with a reserved `example.com` address (which
sends no real mail but still advances, because of the no-enumeration behaviour):

- The masked destination came back from the real server (`vi***@example.com`)
- The countdown started at `04:59`, ticking from the server's `expiresInSeconds`
- Typing the fourth digit auto-submitted with no button press
- The gateway rejected it, `invalid or expired code` rendered in the gold error
  banner, and the field cleared
- Light and dark both correct — the countdown renders navy on light, because
  gold as text on light fails contrast (palette rule R3)

**Not proven:** a *correct* code. That needs someone to read the inbox for
`munyira851@gmail.com` and type the code within 5 minutes.

---

## A bug the tests could not have caught

On Android the code field **did not take focus on arrival** — the member landed
on the pane with no keyboard. iOS was fine.

`LaunchedEffect(Unit) { focusRequester.requestFocus() }` runs straight out of
composition, before the focus modifier is attached during layout, so it silently
did nothing. Fixed by waiting a frame (`withFrameNanos {}`) and then also asking
for the keyboard.

This was invisible to every text assertion — the pane rendered perfectly. It was
only visible by driving a real device. Now pinned by
`theCodeFieldTakesFocusOnArrival`.

Second time this lesson has landed (the clipped carousel tile was the first).

---

## Open issues / next steps

1. **A real end-to-end code sign-in is unverified.** Needs the inbox.
2. **`countryISO2` is sent as `null`.** Optional, and the web client does the
   same, but nobody has said what it is *for*. If it affects routing or
   jurisdiction we should send something real.
3. **4 vs 6 digits** — following the live system over the design reference.
   Worth confirming with whoever owns the design.
4. **Signed-out-elsewhere has no explanation.** The reference shows "Your
   account was opened on another device"; we show a generic expiry message.
   `mySessionStatus { status reason }` exists and returns `another_device` — a
   contained follow-up.
5. **SMS is built but unexercised** — no dev account has a verified phone, so
   `maskedPhone` is always null and the channel switch never appears.
6. Registration 08–12 is now the remaining Phase 3 work.
