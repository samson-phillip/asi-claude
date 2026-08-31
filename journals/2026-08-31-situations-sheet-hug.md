# 2026-08-31 — Situations sheet: hug the content (iOS)

## Report

The "Your most common situations" bottom sheet (27B, reached from Home's Change
link) showed a **large empty gap below the content** — with only two incident
tiles, the card filled most of the screen and left dead space under the Done
button.

## Root cause

`SituationsSheet` wrapped its content in a `ScrollView` inside the `FloatingSheet`:

```swift
FloatingSheet { ScrollView { VStack { …tiles… } } }
```

`FloatingSheet` sizes itself by **measuring its content** and hugging it (capped
at 90% of the screen). A `ScrollView` is greedy — it reports the full proposed
height — so the measurement came back as ~full screen, the card grew to the 90%
cap, and the short content left a gap. This is the exact trap the FloatingSheet
hug fix called out ("re-adding a ScrollView here would make it greedy again");
the nudge and trial sheets avoid it by being plain VStacks.

## Fix

Dropped the `ScrollView` — the sheet content is now a plain `VStack`, so
`FloatingSheet` measures its natural height and hugs it. One file:
`Feature/Situations/SituationsSheet.swift`.

Android is unaffected: its `FloatingSheet` is a native `ModalBottomSheet` and the
Kotlin sheet's `Column` is `fillMaxWidth().verticalScroll()` with **no**
`fillMaxHeight`, so it already sizes to content. No Kotlin change.

## Note / trade-off

Without the ScrollView, a very long incident-type list (well past the ~2–8 that
exist) could exceed the 90% cap and clip. That's not the case with the current
data, and it matches how the other short sheets work; if the incident catalogue
ever grows large enough, this sheet (and the connect tray, which keeps its
ScrollView for the same reason) would want the measured hug-or-scroll treatment.

## Verification

Builds clean. Couldn't screenshot on the sim (its session had ended — login
screen — and I don't use sim credentials). The fix is the same plain-VStack
pattern already **verified hugging** on the sim for the nudge/trial sheets, so
confidence is high; eyeball once logged in.
