# 2026-08-19 — Screen 14 rebuilt to the supplied design

## Task

Run the app and look at it. Then, given a screenshot of the reference's
Upload-documents screen, match it.

Repos touched: `kotlin`, `swift`, `asi-claude`.

## Running it turned up two bugs before any design work started

### 1. The checklist never reached screen 14

Tapping "Upload your documents" on the checklist opened the **setup wizard at
step one — "A few personal details"** — a step already ticked on that same
checklist.

`documentsStep` existed and was reachable from the home nudge and the
notifications feed, but the checklist row itself fell through a `default:` /
`else` branch into the wizard. So the screen built last session was unreachable
by the one route a member would actually take, and the previous commit message
claiming "the checklist and nudge both routed to it" was wrong about the
checklist half.

`ProfileStep.Situations` fell through the same branch, so "Your common
situations" was mis-routed identically. Both fixed on both platforms.

### 2. The way back disappeared exactly when it was needed

With no document sections loaded, the empty state returned early (Android) or
sat in the `else` branch (iOS), so **"Done — back to checklist" never rendered**,
and the header's "Close" went to Home rather than to the checklist. A member with
nothing on file — the most likely person to have arrived from the checklist —
reached the step and lost the checklist they came from. That is the exact dead
end the screen was built to remove.

The button now renders in both states, and in checklist mode Close returns to the
checklist.

## Matching the design

Verbatim reference (`notes/design-reference-codepen.md` §14) against what shipped:

| Reference | Before | Now |
|---|---|---|
| "shareable with your **Law Firm Representative**" | "your attorney" | matches |
| "Add the rest any time — **or mark this step complete below.**" | "Add the rest any time." | matches |
| Four rows, icon + status pill + View/Add | already correct | unchanged |
| "Mark documents as complete" checkbox | **not built** | built |
| "Done — back to checklist" | present | present |

The row treatment needed no work — the Glovebox rebuild had already produced the
bordered card at radius 12 the reference draws.

**The blue `View` / `Add` links stay gold.** The reference sets them in a mid
blue; `design/color-system.md` outranks the CodePen on colour and rules blue out.

**"Law Firm Representative" is the reference's wording on this screen only** —
every other screen says "attorney". Matched here as asked; worth a decision about
which is right app-wide.

## The checkbox, and what it cost to build honestly

Last session I left this control out and logged it as backend-gaps question 8:
nothing on the server stores a per-step completion, so a tick would revert on the
next load. Asked to match the design, I built it — and the reference note settles
what it has to do:

> "The member can mark the step complete even with a partial upload; Done returns
> to the checklist with the box checked."

So it must survive a reload. It is stored **on the device**, in the per-member
defaults store that already holds nudge and tour state (`StepCompletionStore`,
a third role for `UserDefaultsNudgeStore` / `PrefsNudgeStore`). Readiness applies
it through `markingDocumentsComplete(_:)`, which only ever *adds* completion and
never un-ticks a step the documents themselves satisfy.

**The limitation is real and unchanged:** device-local means it does not sync.
Tick it on the phone, open the tablet, and the step is outstanding again. The
backend gap is now narrower, not closed — recorded against question 8.

## Two mistakes worth recording

**A silent `str.replace` shipped nothing.** The Android checkbox landed in the
empty-state branch but not the populated one, because that patch matched on an
indentation that did not exist and I had not asserted the anchor. The render test
caught it — the semantics tree had every string on the screen except
"Mark documents as complete". Anchors get asserted; the one that was not is the
one that failed.

**The iOS stub payloads were invented rather than copied**, so the render loaded
zero sections. The real wire shapes were already in `GloveboxViewModelTests`.

## Verifying it

The emulator and simulator were both signed out by the test runs (see below), so
the populated screen was rendered from fixture state rather than driven live:

- Android — `ScreenRenderTest.uploadDocumentsStepMatchesTheReference`, run via
  `am instrument` rather than gradle so the teardown did not delete the capture.
  Renders all four reference sections with their true icons.
- iOS — `ScreenRenderTests.screen14RendersTheChecklistStep`, an `ImageRenderer`
  pass over a stubbed view model. **Passes, but the PNG could not be retrieved**:
  the test runs on an ephemeral clone simulator whose container is deleted after
  the run. So iOS parity is verified by code and by assertion, *not* by eye —
  the one gap left in this task.

## Tests

| Suite | Result |
|---|---|
| Android unit | **440 / 440**, 0 failed (+7) |
| Android instrumented | **31 / 31**, 0 failed (+1) |
| iOS unit | **429 / 429**, 0 failed (+7) |

One **pre-existing** failure, not from this work:
`DynamicTypeUITests.testLoginStaysUsableAtTheLargestAccessibilitySize`. Confirmed
by stashing every working-tree change and re-running — it fails on clean HEAD
too. Spun out as its own task.

## Open

1. **The tick does not sync across devices** — backend-gaps §8.
2. **"Law Firm Representative" vs "attorney"** — one screen now disagrees with
   the rest of the app.
3. **iOS screen 14 has not been seen** — needs either a signed-in simulator or a
   non-parallel test run to retrieve the render.
4. **The pre-existing Dynamic Type failure on sign-in.**

## A working constraint, now recorded in memory

Both suites sign the device out — gradle's `connectedDebugAndroidTest` uninstalls
the app, and an `xcodebuild test` including the UI tests clears the simulator.
Signing back in is not something I can do; only the user can. So the suites run
*before* visual checks, and screens that need auth get fixture-state renders
instead.
