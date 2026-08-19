# 2026-08-19 — Home situation tiles rendered ragged (Android only)

## Task

Reported against an Android Home screenshot: the "your most common situations"
tiles are unevenly shaped. Repos touched: `kotlin`, `asi-claude`. **iOS was
already correct and is untouched** (see the misstep below).

## A wrong first guess, corrected

I first read this as a *height* problem — labels of different length wrapping to
different line counts — and "fixed" it by reserving two title lines
(`minLines = 2`) on both platforms. That was wrong twice over:

- It didn't fix Android — the report came back that the tiles were still ragged.
- It changed iOS, which was already even. Reverted; the iOS `HomeScreen.swift` is
  back to its committed state with no diff.

The lesson: I diagnosed from the code I *expected* to be rendering
(`IncidentGrid`) instead of the one actually on screen.

## The real cause — the chosen-situations grid never filled its cell width

The screenshot's header is "YOUR MOST COMMON SITUATIONS" with a "Change" link, so
`hasChosenSituations` is true and the composable on screen is **`SituationSlots`**,
not `IncidentGrid`. There, the tile is built as:

```
Box(Modifier.weight(1f)) {
    IncidentTile(type = type, onClick = { … })   // no width modifier
}
```

`IncidentTile`'s column takes the modifier it is given and never calls
`fillMaxWidth` itself. The full-list grid passes `Modifier.weight(1f)`, so its
tiles fill the cell — but `SituationSlots` passed **nothing**, so each tile shrank
to *its own label width*. "Domestic" came out narrow, "Pedestrian Stop" wide, and
the grid read ragged. A **width** problem — which is exactly why the two-line
title change did nothing.

**Why iOS was fine:** its `SituationSlots` uses a `LazyVGrid`, whose cells fill
their column width by construction. Only the hand-rolled Android `Row` + `Box`
grid had the gap.

## The fix

One line: pass `Modifier.fillMaxWidth()` to the tile in `SituationSlots`, so it
fills its half-width cell — the same thing the full-list grid already does with
`weight(1f)`, and the analogue of what iOS's `LazyVGrid` does. Android only.

At half width the labels sit on one line (as they do on iOS, which is even), so
heights come out equal once the widths do; no line-reservation or `IntrinsicSize`
trick is needed.

## Left as a noted follow-up, not fixed

When fewer than three situations are chosen, a row pairs an `IncidentTile`
(content height) with an `AddSituationSlot` (`aspectRatio(1.35f)`), so those two
can still differ in height. Not in the reported screenshot (three tiles, no add
slots), and out of scope here; flagged rather than folded in.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` | **BUILD SUCCESSFUL** |
| iOS | untouched — `HomeScreen.swift` has no diff |

The Android **instrumented** `ScreenRenderTest` renders Home but was **not run**:
it uninstalls the app and would sign out the emulator the user is on. The fix is
layout-only and no unit test covers tile geometry, so the on-device look — every
chosen tile the same width — is the user's to confirm. Given I already shipped one
wrong guess here, that confirmation matters before this is called done.

## Next

Once confirmed, the remaining tab to bring to the reference is
**Activity (screen 32)**.