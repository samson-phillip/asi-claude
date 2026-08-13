# 2026-08-13 — Common situations (screens 13B, 13C, 27B)

## Task

Build the common-situations screens, now that `setMyCommonSituations` shipped.

## Outcome

**Built on both platforms and verified end to end against dev.**

| Screen | Status |
|---|---|
| 13B — Home · situations saved | Built |
| 13C — Common situations · select up to three | Built |
| 27B — Hold a tile · customize your three | Built as the **same** screen as 13C |

Chose three on the Android emulator, opened iOS, and the same three were there —
cross-platform through the backend, for free.

---

## The operation, probed before building on it

The backend shipped `myCommonSituations` / `setMyCommonSituations` without
telling us; we found them looking for trial operations.

| Probe | Result |
|---|---|
| Save three, read back | ✅ order preserved |
| Save five | ❌ `you can save at most 3 common situations` |
| Save an unknown id | ❌ `unknown incident type` |
| Save `[]` | ✅ clears the selection |

**Notably better validated than `addSubaccount` was** — that one accepted an
all-zeros price id and created a seat billing against nothing (A7). This rejects
a bad id outright, which is what we asked for and what the backend said they had
done.

---

## Decisions

**One picker, two entry points.** 13C is reached from the setup checklist, 27B
from Home — the Change link or an empty slot. The design describes the same grid,
the same cap and the same copy in both, so two screens would only be two things
to keep in step.

**The fourth tap is ignored.** The design is explicit: *"the fourth tap is
ignored until one is released. To swap a situation, tap a selected tile to remove
it and then pick another."* Evicting the oldest choice silently is helpfulness
nobody asked for. Unchosen tiles dim once three are picked, so a tap that does
nothing is explained rather than mysterious.

**The screen renders what the server kept, not what we sent.** It collapses
duplicates and enforces the cap, so the two can differ — and the backend told us
to do exactly this.

**An empty result means "no choice saved", and Home falls back to the full list.**
An unreadable result looks identical, which is the right way round: being one tap
from an attorney matters more than showing the right three.

**A saved id with no matching type is dropped** rather than becoming a phantom
selection a member can neither see nor clear.

**Readiness carries the chosen ids.** Readiness needs to know *whether* any
exist; Home needs *which*. Fetching separately meant a second round trip on the
app's hottest screen for data we already had — caught by the test that counts
requests, not by looking.

---

## Situations joined the readiness checklist

The step was held back with an explicit reason in the code: *"it has no
operations at all, and a step nobody can complete would sit at 0% forever."* That
reason is gone, so it is in — exactly as Documents went in when the types were
seeded.

That moved every percentage in the app. Thirteen tests failed, all of them
encoding the old shape, and they were worth fixing individually rather than
bulk-bumping numbers:

- **One asserted the *absence* of a situations row.** It has now twice asserted
  the opposite of the truth — first for documents, then for situations. Inverted
  rather than deleted, so the history stays visible: a row appears exactly when
  something stands behind it.
- **Two hardcoded lists of steps** (the nudge copy check, the silence-everything
  check) now derive from the enum, so a new step cannot ship with placeholder
  copy or slip past the silencing test.

---

## Files touched

**`kotlin`** — `core/network/AsiApi.kt` + `NotificationModels.kt` (two
operations), `core/profile/ProfileReadiness.kt` (the step and the carried ids),
`core/nudge/NudgePolicy.kt` (priority and copy), `feature/situations/` (new),
`feature/home/` (three slots, the Change link, dashed empty slot),
`MainActivity.kt`.

**`swift`** — the same, plus `Feature/Situations/`.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **335 pass**, 0 fail |
| iOS unit | **317 pass**, 0 fail |

Coverage: pre-selection in stored order, dropping an id with no type, toggling,
the ignored fourth tap, releasing to make room, the remaining count flooring at
zero, sending in order, the server's list winning, no-op when unchanged, clearing
being a real change, a refused save keeping the selection, and an unreadable
choice still offering everything.

### Verified on emulator and simulator

The Situations nudge fired on Android (readiness had dropped to 75%), opened the
picker, three chosen with the fourth tap correctly ignored, saved, and Home came
back with "YOUR MOST COMMON SITUATIONS", the three tiles in the order picked, a
Change link, and 87%.

On iOS the *PIN* nudge fired instead — because situations were already done on
the account — and Home showed the same three tiles at the same 87%.

---

## Open issues / next steps

1. **Holding a filled tile does not open the picker.** The design mentions
   press-and-hold as one of 27B's entry points; the Change link and empty slots
   both work. Worth adding.
2. **No press-flash on the tiles.** 27A describes a press-flash for direct
   connect; our tiles route through the confirmation sheet (28), which is the
   other path, so this may not apply.
