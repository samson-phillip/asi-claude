# 2026-08-14 — B8b: `kind`, app state, and a defect it uncovered

## Task

B8b, the low-priority remainder of B8: what `kind` is supposed to mean, and
somewhere to store per-member app state that is not a preference (tour-seen,
per-nudge "don't remind me").

**Neither half has shipped.** Probed before assuming: `kind` is still an
undocumented free string with no enum anywhere in the schema, and there is no
JSON/state column on `UserProfile` or anywhere else.

So the honest answer to "build B8b" is that most of it cannot be built yet. What
*could* be done was to look properly at what we do today instead — and that
turned up a real defect needing no backend at all.

## The defect: state was per install, not per member

Both platforms keyed tour-seen and nudge state to the **installation**:

```
asi_nudges: tour_seen, silenced, rest_<step>          (Android)
asi.tour.seen, asi.nudge.silenced, asi.nudge.rest.*   (iOS)
```

Sign-out did not clear any of it.

**The plan supports family sub-accounts** — the Profile screen literally says
"Family members · 0 of 2 on your plan" — so two people sharing a phone is an
ordinary case, not an exotic one. And in that case the second member to sign in
inherited the first member's state:

- **No guided tour**, because someone else had already seen it. A brand-new
  member got no onboarding at all, silently.
- **No nudges**, because someone else had dismissed them. Never reminded to add
  an emergency contact.

The second one is the one that matters. A member who never gets nudged to add an
emergency contact, because a relative dismissed that nudge on the same handset,
is a safety gap produced by a storage key.

### The fix

Keys are scoped to the signed-in member, read **at each access** rather than
captured — the store is built before sign-in and survives sign-out, so a
captured id would be stale exactly when it matters.

Signed out, everything lands in an `anon` bucket. Nothing meaningful is written
there (there is no tour and no nudge without a member); it exists so the keys
stay total, and there is a test that it never leaks into a real member's scope.

This also matches the shape of the server-side store we asked for, so moving
this off the device later is a swap rather than a rewrite.

### A small design change to make it testable

Android's store talked to `SharedPreferences` directly, which would have meant
pulling in Robolectric to test any of this. The few operations it needs are now
behind a `KeyValueStore` interface with a real implementation and an in-memory
one — so the scoping rules, which are the interesting part and pure key
arithmetic, are testable in a plain JVM test. iOS already injected
`UserDefaults`, so it needed only the closure.

## `kind` — a better question than the one we asked

Re-checking made the ask sharper rather than answering it.

`createNotification` still accepts anything (`"totally-made-up-kind"` goes
through). But the test member's inbox came back **empty**, and every notification
we have ever seen on dev was one *we* created while probing. **Nothing on the
backend produces notifications.**

So there is no vocabulary to discover, and "what does `kind` mean?" was the
wrong question. The ask is now: *when something starts producing notifications,
tell us the set of `kind` values it will use.* Three or four (`setup`, `tip`,
`billing`, `safety`) would let screen 24 render the icons and grouping the
design draws. Until then we use one generic treatment — plain, but honest.

## Test results

**Android — 410 tests, 0 failures.** **iOS — 387 tests, 0 failures.**

New: `PrefsNudgeStoreTest` / `NudgeStoreTests`, 5 each — the tour, dismissed
nudges, resting timers and the master switch all per member, plus the signed-out
bucket not leaking.

## What is not verified on device

The cross-member case needs **two** member accounts, and we have credentials for
one. The behaviour is covered by tests on both platforms against real storage
(an in-memory `KeyValueStore` on Android, a throwaway `UserDefaults` suite on
iOS), and the change is a key prefix rather than logic — but I have not watched
member B sign in on a device member A used.

Worth doing once there is a second usable account. Same blocker as the trial
screens.

## Open issues / next steps

- **B8b stays open on the backend**, restated in `notes/backend-asks.md` with
  the sharper `kind` question and the app-state ask.
- **A second test account** would unblock this verification *and* the trial
  screens. Currently the only usable credentials are `munyira851@gmail.com`;
  `tester6@ainnop.com` has no known password.
- Still open from earlier today: a short-lived-token switch on dev so C2's
  refresh can be exercised on a device; the two schema-vs-dev discrepancies
  (`completeMyOnboarding` not idempotent, `otherSessionsRevoked` not revoking).
- Screens **08/09** still need a real phone number for live verification.
- With David: emergency-contact alert, guest model, specialty ordering.
