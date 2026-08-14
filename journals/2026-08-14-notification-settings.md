# 2026-08-14 — B8 and screen 26: the categories and the frequency dial

## Task

Finish design screen 26. It has four category toggles and a "How often" dial;
until today `UserProfile` carried **two booleans**, neither of them a category,
so only the master switch had anything behind it and the rest were left out
rather than wired to a field that means something else.

That gap was **B8** in `notes/backend-asks.md`. The backend's round-2 note says
it landed.

## Repos and files touched

### `kotlin`
| File | What |
|---|---|
| `core/network/NotificationModels.kt` | `NotificationFrequency` enum; four new fields on `NotificationPreferences`; `categoriesApply` and `pausedNote`. |
| `core/network/AsiApi.kt` | Read and patch all six fields. |
| `core/design/AsiComponents.kt` | **New** `AsiSegmentedControl`. |
| `feature/notifications/NotificationsViewModel.kt` | `setPreferences` takes all six. |
| `feature/notifications/NotificationsScreen.kt` | The full screen 26. |
| `MainActivity.kt` | Four new callbacks. |
| `feature/notifications/NotificationsViewModelTest.kt` | 7 new tests. |

### `swift`
Same shape, plus `AttorneyShieldTests/NotificationsViewModelTests.swift` —
**new**, and filling a real gap: iOS had no coverage of this view model at all,
while Android has had it since the centre was built.

### `asi-claude`
`notes/backend-asks.md` — B8's first half closed; the `kind` question and the
app-state gap stay open.

## What the schema actually says

Probed before building, not assumed:

```
notifySetupReminders   Boolean
notifyTips             Boolean
notifyAccountBilling   Boolean
notificationFrequency  String   "occasionally | rarely | off. Anything else is rejected."
```

Two things worth recording:

- **The validation is real.** `notificationFrequency: "whenever-i-feel-like-it"`
  comes back as `notificationFrequency must be one of: occasionally, rarely,
  off`. Checked rather than trusted — A7 was a field the gateway *said* nothing
  about and silently accepted garbage for. This one behaves.
- **It is case-insensitive and normalising.** `"OFF"` is accepted and stored as
  `"off"`. The app still sends lowercase; an enum with a `wire` value makes a
  typo a compile error instead of a rejection in front of a member.

The backend also wrote our own warning into the schema:

> marketingOptIn → "Marketing CONSENT, with legal weight. Do NOT use it to store
> the design's 'Tips & know-your-rights' toggle — that is `notifyTips`."

That is the ask coming back as documentation, which is the best possible outcome
for it.

## Decisions

### `marketingOptIn` stays its own row

Still labelled "Marketing emails", still last, still apart from the four
categories. It is a consent record, not a content preference, and now the schema
says so too.

### The dial is an enum, the wire is a string

`NotificationFrequency` has a `wire` (`occasionally`) and a `label`
(`Occasionally`). Sending the label would be rejected. An unrecognised value read
back falls to the **default, never to Off** — telling a member their
notifications are off when we merely failed to parse the value is the one wrong
answer, and it is the same rule the preference read already follows for an
unreachable profile.

### One row at a time

`updateMyProfile` patches, so only the control that moved is sent. That matters
more here than elsewhere: this screen saves per row, and a full-object write
would let a stale copy of the screen revert a change made on another device.
Asserted on the request *variables*, not on the body — the query's own selection
set names every field, so a substring check would pass no matter what was sent.

### Paused is said, not shown by disabling — a correction

The first version disabled the three category rows while the master switch was
off or the dial was on Off. On the emulator they looked **completely normal** and
simply stopped responding to taps.

The cause: `AsiSwitchRow` deliberately draws a disabled-but-on switch exactly
like a live one. That was written for the Safety-critical row, where "always on"
is the whole point of showing it. Reusing `enabled = false` for "your choice,
currently paused" gave one visual two meanings, and on Android the second one was
invisible.

The rows are live again, and a line above them says what is happening:

> How often is set to Off, so these are paused. Your choices are kept.

Better product behaviour as well as clearer: a member can set up what they want
to hear *before* switching notifications back on, and nothing they choose is
lost. The note names the specific control that caused it — the master switch
takes precedence when both are off, because that is the more useful one to point
at.

## Test results

**Android — 375 tests, 0 failures.** **iOS — 357 tests, 0 failures.**

The three `DynamicTypeUITests` failures remain the pre-existing ones from
2026-08-13; they assume a signed-out simulator.

**One iOS test passed for the wrong reason and was fixed.** The "unreadable
preferences read as defaults" case queued a 500 *behind* a good 200. The stub
matches on content, so the 200 answered the request and the 500 was never
reached — the test proved nothing. The failure is now the only queued response
for that request.

## Verified on device

Genuinely end to end, and across platforms:

1. iOS: tapped **Rarely** → `notificationFrequency` on dev became `"rarely"`, and
   nothing else on the profile moved.
2. iOS: tapped **Off** → the three category rows kept their values, the paused
   note appeared, the master switch and Marketing stayed live.
3. Android, launched fresh: read `"off"` back from the server — the value iOS
   wrote — and showed the same note.
4. Android: tapped **Occasionally** → note gone, dev back to `"occasionally"`.

## Open issues / next steps

- **B8's second half is still open:** what `kind` is supposed to mean.
  `createNotification` still accepts any string. We carry it through and group
  loosely rather than switching on it.
- Also still open from B8: nowhere to store per-member **app state that is not a
  preference** — tour-seen, and "don't remind me" per nudge. Both live in device
  storage and do not follow a member to a second phone.
- **B2 is now unblocked and unbuilt:** `pronouns` exists on `UserProfile`
  ("Member-supplied, e.g. \"she/her\". Never derived from `gender`.") — that is
  the last field of screen 10.
- Still queued: **B4** (notify-by, screen 16), **C8**, **C2** (token refresh).
- Trial screens **V2, T5–T8** remain unverifiable without a password for
  `tester6@ainnop.com`.
