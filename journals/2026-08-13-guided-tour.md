# 2026-08-13 — The guided tour (screens 17–21)

## Task

Build the tour screens.

## Outcome

**Built on both platforms and walked end to end on device and simulator.**

| Screen | Status |
|---|---|
| 17 — Guided walkthrough · step 1 | Built |
| 18 — Step 2 · Glovebox | Built |
| 19 — Step 3 · Activity | Built |
| 20 — Step 4 · notifications | Built |
| 21 — Tour complete | Built |

No backend at all: this is the first block that needed none.

---

## The spotlight rings the real element

The design asks for the focused element to be "lifted above" a dimmed backdrop,
"so there is never a question of what the tour is pointing at."

Rather than clone the element, the scrim is **punched through at its real,
measured bounds** — what shows in the hole *is* the live element. Home reports
where the shield hero and the bell landed; the tab bar reports where it put the
Glovebox and Activity tabs. Android uses `onGloballyPositioned` + `boundsInRoot`,
iOS a `PreferenceKey` carrying `frame(in: .global)`.

A hard-coded rectangle would have been right on exactly one device and wrong the
first time the layout, the text size or the screen changed. The tab bar is the
clearest case: it lays its tabs out evenly, so a caller guessing "a quarter of
the width" would be right today and wrong the moment a fifth tab appears.

The coach card sits opposite the spotlight — measured against the real screen
height, not a pixel constant — because a card covering the thing the tour points
at defeats the exercise.

---

## Three bugs the device found and the tests could not

### 1. The overlay did not block touches

The scrim was a `Canvas` with no pointer input. The first "Next" went straight
through it to the **Activity tab** and navigated out of the tour.

A walkthrough you can tap out of by accident is not a walkthrough. Both platforms
now swallow every touch that is not the card's own.

### 2. The coach card sat under the navigation bar

"Replay anytime from Settings" was cut in half on Android. The scrim *should*
cover the system bars — it is a scrim — but the card should not. Only the card is
inset now.

### 3. The same bug on iOS, for a different reason

`safeAreaPadding()` resolves to nothing once an ancestor has called
`ignoresSafeArea()`, so the card rode under the status bar. The scrim and the
card are now siblings: the scrim ignores the safe area, because it is positioned
from global frames; the card does not.

Worth noting all three are *layout* bugs. Unit tests covering step order, copy
and state transitions all passed throughout.

---

## Decisions

**The pulse stops under reduced motion.** It is decorative and it never ends,
which is exactly what that setting exists to stop. The reference sets the
precedent itself — the connecting screen's rotating tips "pause under reduced
motion". Android reads `ANIMATOR_DURATION_SCALE`, iOS
`accessibilityReduceMotion`.

**A nudge cannot fire during the tour.** Two overlays arguing over one screen,
and the tour is the one the member did not ask for twice. It is the same "wait
for a calm moment" rule the nudge policy already has. Verified on both platforms:
finish the tour, relaunch, and the nudge takes its turn.

**The tour only ever runs over Home.** All four targets live there; following the
member into the Glovebox would ring things that are no longer on screen.

**`Done` is part of the tour, not the end of it.** Screen 21 is a state, so
`isActive` stays true over the celebration card — which is what stops a nudge
appearing on top of the congratulations.

**Seen-state is device-local.** Nothing member-facing in 238 queries and 297
mutations can hold it. The design says "first launch", and for a per-install tour
that is a defensible reading — but a member on a second phone sees it again.

**Settings gained the Replay row** the tour's own footer promises. It returns to
Home first, because a spotlight over Settings would ring nothing.

---

## Files touched

**`kotlin`** — `core/tour/TourStep.kt` (new), `core/nudge/NudgeStore.kt` (now also
the `TourStore`), `feature/tour/TourOverlay.kt` (new),
`core/design/AsiComponents.kt` (tab bounds), `feature/home/HomeScreen.kt`
(hero and bell bounds), `MainActivity.kt`, `feature/account/AccountScreen.kt`.

**`swift`** — the same, plus `Feature/Tour/TourAnchors.swift` for the preference
that carries frames to the root.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **320 pass**, 0 fail (was 311) |
| iOS unit | **303 pass**, 0 fail (was 293) |

Coverage: the four steps and their order, the one-based counter, Next/Finish,
walking to the end in exactly four taps with no repeats, distinct targets, copy
present on every step, `Done` counting as active, and both stores round-tripping
including the real `SharedPreferences`/`UserDefaults` ones.

### Verified on device and simulator

Walked all five screens on both. Confirmed the ring lands on the shield, the
Glovebox tab, the Activity tab and the bell; that the card moves to the opposite
end when the target is at the bottom; that Skip and Finish both end it; that it
does not return on relaunch; and that the nudge appears only afterwards.

---

## Open issues / next steps

1. **Seen-state does not sync across devices** — no field for it (added to the
   backend asks alongside the nudge's "Don't remind me").
2. **No blur, only a dim.** The design says "blurs and dims". A real backdrop
   blur costs a render pass on every frame of a pulsing animation; the dim plus
   the gold ring already makes the target unmistakable. Worth revisiting if the
   design team feels the difference.
3. **The tour cannot be entered mid-flow from a nudge or the checklist** — only
   first launch and the Settings row. Nothing asks for more yet.
