# 2026-08-17 — Guest sign-up confirmed end to end

## Task

Close the question left open since 2026-08-16: does an account created from the
mobile app actually come back as `guest_user`? The `origin: APP` wiring was
tested against the wire but never against the live gateway.

## Result — confirmed

```
userId=54b146bb-8a39-4394-be82-62d3f7216b03
roles=[Member]
accountStatus=guest_user / "Guest User"
```

**`origin: APP` does what it was supposed to.** An account created from the app
is segmented as a Guest User, not a Member Lead. Everything written in
backend-gaps §9 was against the schema; this is the first observation from the
live gateway.

## How it was done

A brand-new email was taken through the app's own OTP flow on **iOS** (the user
ran it), which created the account — "Account created" ticked, session live.
That alone could not prove segmentation: iOS keeps the session in the Keychain,
which is encrypted even in the simulator (checked directly — service, account
and data columns are all ciphertext).

So the account was read back by signing into it on **Android**, which carried a
temporary read-back. That is a read, not a write: `origin` is only consulted on
the verification that *creates* an account, so signing into an existing one
cannot change its segmentation.

The read-back is now removed. It was never committed.

## Two faults worth recording

- **`android.util.Log` broke five unit tests.** The first version of the
  read-back used it; `Log` is not mocked in JVM unit tests, so every sign-in
  fixture threw. The second used `println`, which reaches logcat on device via
  `System.out` and is harmless in tests — 433/433 passed with it in place.
- **There are two Attorney Shield apps on the emulator.** A legacy build sits at
  `com.app.attorney.shield` (white splash, red/blue branding); ours is
  `com.app.attorney.shield.debug`. A package lookup that did
  `grep -i attorney | head -1` picked the legacy one — which is also why an
  earlier attempt to read a capture file off the device found only Firebase
  files. **Always use the `.debug` suffix for adb work here.**

## What this settles as a side effect

- **Self-serve sign-up genuinely works from the app.** No web hand-off: the OTP
  flow creates the account on first correct code.
- **`myAccountStatus` is readable by a plain member** — self-scoped from the
  token, so unlike `statusCodeList` it needs no elevated permission.
- **Question 5 is partly answered.** New accounts are stamped immediately, so
  the null-status fallback is not exercised by new sign-ups. Whether
  *pre-migration* accounts have been reconciled is still unknown.

## Still open

- **What a Guest User may actually do** (question 3) — nothing in the UI reacts
  to guest status yet, because what a guest is *allowed* to do is undecided.
  The status is stored and re-read on refresh; that is all.
- **How a guest converts** (question 4) — no trial-start operation exists.
- **The status code list** (question 2) — `statusCodeList` needs a permission
  members do not hold, so the app still cannot enumerate codes; `guest_user` is
  known only because it was observed.
- **The sign-up copy still says "Welcome back."** The flow works, but a
  first-time user is greeted as a returning one. No sign-up-specific screen
  exists yet.

## Files

- `kotlin`: `SessionManager.kt` (temporary read-back added and removed — no net
  change committed).
- `asi-claude`: `notes/backend-gaps.md` §9 gains a "Confirmed end to end"
  section; questions 1 and 5 updated.

## Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
