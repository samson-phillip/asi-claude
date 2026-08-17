# 2026-08-17 — Sign-up copy

## Task

The OTP screen greeted every member with "Welcome back." even though a new
address creates an account there — confirmed against the live gateway earlier
today.

## What changed

Only the **email pane**, on both platforms:

| | Before | After |
|---|---|---|
| Eyebrow | SIGN IN | SIGN IN OR SIGN UP |
| Title | Welcome back. | Start with your email. |
| Body | Enter your email and we'll send you a secure sign-in code. | We'll send you a secure code. If you're new, that code creates your account. |

**The password pane keeps "Welcome back."** A password only exists for an
account that already exists, so there the greeting is simply true. Changing it
would have been wrong.

## Why the copy says what it says

Two reasons, and the second matters more than the tone:

1. **The app cannot tell a new email from an existing one.** The gateway does
   not enumerate accounts — an unknown address returns `sent: true` with the
   address masked back (backend-gaps §3). So greeting everyone as returning is a
   guess that is wrong half the time, and there is no way to make it right at
   this step.
2. **It hid a real consequence.** A mistyped address does not fail here; it
   provisions an account. The new body says so plainly.

Nothing after this step needed changing: "Verify it's you." is already neutral,
and a fresh sign-in lands on the completion checklist, which reads correctly for
a new member ("Account created ✓") and a returning one alike.

## Two things noticed while verifying

- **The iOS Keychain survives app uninstall.** Deleting and reinstalling the app
  left the session intact and dropped straight back into Home. That is standard
  iOS behaviour, not a bug in our code, but it means uninstall is not a way to
  reset a test device, and on a shared or resold device a session outlives what
  a member would reasonably expect. Signing out through Profile is the only real
  reset. Worth a decision on whether to clear the Keychain on first launch after
  install.
- **The signed-up account reads as expected.** Profile shows the address and
  "Your membership — Not covered", consistent with a Guest User holding no plan.

## Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **417 / 417**, 0 failed |

`DynamicTypeTest` asserted on "Welcome back." and was updated to the new title.

Verified by eye on the Pixel 8a and the iPhone 16 Pro.

## Still open

- **What a Guest User may actually do** — nothing in the UI reacts to guest
  status yet.
- **Whether to clear the iOS Keychain on first launch after install** (above).
