# 2026-09-09 — Enrollment-ladder gate swap (myEnrollmentState) — #159 finished

Follow-on to `2026-09-09-david-v3-159-parity.md`. Samson said "yes, do the gate
swap too", so the deferred §2.3–2.5 headline is now done on both apps
(kotlin `ec51437` / swift `1979585`).

## What made it safe to do

Two findings de-risked what I'd flagged as a launch-path refactor:
1. The gateway **already exposes `myEnrollmentState`** (introspected:
   `MemberEnrollmentState { status(MemberStatusRef), phoneVerified, hasAddress,
   hasSex, hasBirthday, pinSet, pinResetRequired }`), so the port is verifiable.
2. The native checklist is a **soft gate** — `ProfileCompletionScreen` has
   `onClose = navigate(.home)` — so nothing here can strand a member; the swap
   only changes what's auto-skipped on entry and which rows show.

## The change (both apps, symmetric)

- **Primitives** (`Enrollment.kt` / `Enrollment.swift`): `EnrollmentState` +
  `registrationOwed` — a faithful port of `registration.ts`. Fail-SAFE: a nil
  state (field absent / gateway re-introspecting) returns "not owed", so a
  long-standing member is never walked back through the run.
- **`getEnrollmentState()`** on AsiApi — best-effort, nil on any error.
- **`ProfileReadiness`** gains an `enrollment` field; `isOnboarded` is now
  `!registrationOwed(enrollment)` when present, else the old `flag || allDone`
  fallback. So the §2.3 minimum (verified phone + address + sex + birthday + PIN)
  drops a member to Home even with optional rows (documents/contacts) still open.
- **`pinResetRequired` (§2.5)**: the Security PIN row re-opens for a returning
  canceled/expired member even though a PIN is on file → they finish with a fresh
  one. Wired via the Pin task's `done = pinSet && !pinResetRequired`.
- **Details row now needs a sex**, consistent with the Setup gate shipped earlier.

## Tests

New `EnrollmentTest`/`EnrollmentTests` cover the fail-safe null, the
pinResetRequired path, and the authoritative gate (active onboards despite an
incomplete checklist; owed blocks despite the flag). Existing readiness tests
(Home, ProfileCompletion, Notifications) needed their profile stubs to seed a real
sex (else the new Details rule flips them) and to account for the extra
`myEnrollmentState` read.

**Verification note:** kotlin `:app:testDebugUnitTest` green. The swift **full**
suite once reported Home/ProfileCompletion/Notifications/Glovebox failing — all at
0.000s on the same parallel **simulator clone ("Clone 2")**, including Glovebox
which touches none of this. Re-running each class in isolation: **all pass** (Home
30, ProfileCompletion 56, Enrollment 18, Glovebox 56, Notifications 26). So that
was a clone crash (earlier disk pressure), not a real failure.

## Net: member-client #159 is now fully mirrored

§2.3 Sex required · §2.2 sub-account emails · §2.3–2.5 enrollment-ladder gate +
pinResetRequired. The count repairs were already correct natively (never had the
bug). Nothing outstanding.
