# 2026-08-13 — Notifications and nudges (screens 22–26)

## Task

Build the notification screens.

## Outcome

**Built on both platforms and verified against dev.**

| Screen | Status |
|---|---|
| 22 — Bell · resting | Built |
| 23 — Bell · new nudge | Built |
| 24 — Notification centre | Built |
| 25 — Gentle nudge (bottom sheet) | Built |
| 26 — Notification settings | **Partial** — two of five controls have a field behind them (B8) |

---

## Proven before building on it

The whole chain, live, as the test member:

| Step | Result |
|---|---|
| `createNotification` | ✅ |
| `notificationList` | ✅ |
| `notificationList(unreadOnly: true)` | ✅ |
| `markNotificationRead` | ✅ sets `readAt`, count drops |
| `markAllNotificationsRead` | ✅ returns how many |
| `clearNotifications` | ✅ returns how many |
| Another member's inbox — read | **`forbidden`** ✅ |
| Another member's inbox — write | **`forbidden`** ✅ |

Properly self-scoped, which was the thing worth checking before putting a badge
on the home screen.

Two findings went into `notes/backend-asks.md` as **B8**: `kind` is free-form
(`"totally-made-up-kind"` was accepted), and `createNotification` is callable by
a member for their own inbox — correctly scoped, so not a hole, just odd.

---

## The six ground rules are code, not comments

The reference lists six rules for nudges. They are all *restraints*, and
restraints in view code get quietly lost the next time someone adds a screen —
so they are one pure function, `NudgePolicy.pick`, with a test each.

| Rule | How it is enforced |
|---|---|
| 1. Never blocks the app | A dismissible sheet, declared after the tray and connect sheets so those always win the screen |
| 2. One at a time, capped | `shownThisSession` (view-model lifetime = session); dismissal rests the step for 3 days; "Don't remind me" is permanent |
| 3. Timed to calm moments | `isCalm` — no nudge mid-call |
| 4. Always says why | Copy lives on `Nudge`, benefit first; a test asserts every step has a title, a body over 40 characters and an action |
| 5. Critical items lean in | Emergency contacts are first in the priority list — the one gap with a consequence *during* an encounter |
| 6. Stops when you're done | `allDone` returns nothing; so does an unloaded readiness, so a cold start cannot invent one |

The stakes are in the reference's own words: *"one annoying buzz [is] enough to
lose the notification channel for good."*

---

## Decisions

**The centre's two groups come from different places.** "Finish setup" is derived
from `ProfileReadiness`, not from the feed — those rows carry one-tap actions and
have to vanish the moment the thing is done, where a server-side notification
would sit there stale until someone deleted it. "Earlier" is the real feed and is
read-only.

**The badge reads zero on a failed count.** A badge is a claim that something
needs attention; inventing one from a network hiccup is worse than the quiet bell
the design asks for. It is also capped at `9+` — a badge reading "47" is a to-do
list, not a nudge.

**Marketing opt-in is labelled as marketing.** The design's "Tips &
know-your-rights" toggle has no field. `marketingOptIn` exists and would have
fitted the slot, and mapping it there would have been wrong: it is a consent
record with legal weight, and relabelling a consent as a content preference is
the kind of thing that is discovered during an audit.

**Nudge state is on the device.** There is no field for any of it, and cadence is
a property of *this* install. The cost — "Don't remind me" does not follow a
member to a second device — is recorded rather than papered over.

**Documents joined the readiness checklist.** The step had been held back while
`adminDocumentTypeList` returned `[]`, and the comment saying so was still in the
code. The types are seeded, the Glovebox is built, and the design's notification
centre lists "Upload your documents" as one of its two setup nudges. Percentages
moved from sixths to sevenths and the tests that encoded six steps were updated.

---

## The bug the tests could not have caught

The nudge sheet appeared and vanished about a second later.

`refreshReadiness()` runs more than once per visit to Home. The first call picked
a nudge; the second re-evaluated, got `null` because rule 2's cap was already
spent, and **wrote that `null` over the nudge that was on screen**.

A nudge on screen now belongs to the member until they answer it. Two regression
tests: one that a second refresh leaves it alone, one that snoozing is what
clears it and rests the step.

It only showed up on a device. Thirteen policy tests all passed while it was
broken, because the policy was right — the bug was in what the caller did with
the answer.

---

## A stub key that collided by prefix

`"query User"` is a strict prefix of `"query UserDocuments"`, so the substring
matcher answered the documents read with the user stub. Documents came back
empty, readiness read 6 of 7, and two tests failed with a percentage that looked
like a product bug.

Exactly the same shape as the `"DocumentFields"` collision in the Glovebox tests.
Both suites now key on `"query User("`.

---

## Files touched

**`kotlin`** — `core/network/NotificationModels.kt` (new), `core/network/AsiApi.kt`
(6 operations), `core/nudge/` (new: `NudgePolicy.kt`, `NudgeStore.kt`),
`feature/notifications/` (new: view model, centre, nudge sheet),
`core/design/AsiComponents.kt` (`AsiNotificationBell`, `AsiSwitchRow`),
`core/format/Formats.kt` (`formatRelative`), `core/profile/ProfileReadiness.kt`
(the documents step), Home and `MainActivity.kt`.

**`swift`** — the same structure throughout.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **311 pass**, 0 fail (was 283) |
| iOS unit | **293 pass**, 0 fail (was 279) |

Coverage: all six ground rules, the state bookkeeping and both stores, badge and
unread counting, mark-one and mark-all including the revert on failure, no
pointless mutation when there is nothing to mark, setup items derived from
readiness, preference writes sending only the changed field, and the optimistic
switch reverting when the server refuses.

### Verified on device against gateway-dev

**Android** — two seeded notifications: badge of 2 with the gold glow, the centre
with both groups, "Mark all read" clearing the badge with the server agreeing
(`unreadNotificationCount` → 0), the bell back to its resting state, and the PIN
nudge appearing and staying put.

**iOS** — the same, with a third notification seeded: the contacts nudge, badge
of 1, and the centre with all three items and the settings section.

All seeded notifications were cleared afterwards; the test account's inbox is
empty again.

---

## Open issues / next steps

1. **Screen 26 is two controls out of five.** Categories and the frequency dial
   need fields (B8).
2. **No push.** This is the in-app centre only — no APNs or FCM registration,
   no device token, and nothing in the schema to store one. That is a separate
   piece of work and needs a backend decision first.
3. **"Don't remind me" is per-device.** No field to sync it.
4. **`kind` is not used for anything.** It is free-form and we will not guess;
   once the vocabulary is confirmed it can drive icons and grouping.
5. **The iOS session was revoked mid-verification** by signing in on Android.
   That is the documented one-device-at-a-time rule working as intended, and the
   app surfaced "unauthorized" rather than pretending — but it does make
   verifying both platforms in one sitting a sign-in each way.
