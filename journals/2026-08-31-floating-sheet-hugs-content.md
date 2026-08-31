# 2026-08-31 — iOS bottom sheets: hug the content, not the screen

## Report

The nudge sheet (and the trial sheets) had **huge dead space above and below the
content** on iOS — the content sat vertically centred in a near-full-screen card.
"Make them look professional."

## Root cause

The custom `FloatingSheet` (iOS) sized its card with
`.frame(maxHeight: proxy.size.height * 0.9)`. `.frame(maxHeight:)` doesn't cap a
hugging view — it makes the view **flexible up to that height**, so inside the
GeometryReader/ZStack (which proposes the full screen height) the card **expanded
to 90% of the screen and centred** short content. Every plain-content sheet
(nudge, trial gate, connect confirmation, guest gate) filled the screen with the
content floating in the middle.

(This also explains why last commit's trial fix — removing the ScrollView — only
changed the trial sheet from top-aligned dead-space to centred dead-space: the
real cause was the `maxHeight` frame, not the content.)

Android is unaffected: its `FloatingSheet` is a native `ModalBottomSheet`, which
hugs its content already.

## Fix

`FloatingSheet` now **measures its content height** and sets an explicit
`.frame(height: min(contentHeight, 0.9 * screen))`, so the card hugs its content
and only grows to the 90% cap when the content would actually overflow (then it
scrolls). One central change fixes every sheet:

- Short sheets (nudge, trial gate/notice/pending, connect-confirm, guest gate) now
  **hug their content** — no dead space.
- The tall one (the connect tray, a grid of situation tiles) still keeps its own
  `ScrollView`; it measures as full, caps at 90%, and scrolls — unchanged.

Files: `Core/Design/FloatingSheet.swift` only (added a `SheetContentHeightKey`
preference + content measurement). No Kotlin change.

## Verification

Builds clean. This is a pure layout change to a shared component with no unit
test; **worth an eyeball on the simulator** across a nudge, the trial gate, and
the connect tray to confirm short sheets hug and the tray still scrolls.

## Note

Kept the trial content as a plain VStack (no ScrollView). With the FloatingSheet
fix it hugs correctly; re-adding a ScrollView there would make it greedy again and
reintroduce the dead space on the short gate state.
