# 2026-08-19 — Section detail: the reference's shield watermark

## Task

Two things noticed on the Glovebox section-detail screen (14A-14D) against the
CodePen: the app carries a subtitle below the green pill that the reference does
not, and the reference has a **dim shield watermark** behind the content that the
app lacks. Repos touched: `kotlin`, `swift`, `asi-claude`.

## What the CodePen 14D actually has

Read from source (`code_pen_design.html` ~9740-9783): a `.docbg` layer — the
heraldic shield SVG at **~4% opacity**, absolutely positioned and centred behind
the content — then `.dwrap` with the title bar, the green pill, and **straight
into the fields**. There is **no subtitle** between the pill and the fields.

The app, by contrast, renders `section.description` ("Passport and citizenship
documents") under the pill, and draws no watermark.

## The watermark — added

Both platforms now draw the shield behind the **detail pane only**, fixed to the
viewport rather than scrolling with the content, at 5% opacity to match the
reference's whisper.

- Kotlin — the screen root is now a `Box`: it paints the navy background and,
  when the pane is the section detail, an `Image` of `ic_brand_shield` centred at
  `alpha(0.05f)`; the scrolling `Column` sits transparent on top. Drawn as an
  `Image`, not a tinted `Icon`, so the heraldic mark keeps its own colours the
  way the CodePen's does.
- iOS — a `.background(alignment: .center)` on the detail `ScrollView` with
  `Image("brand_shield_hero")` at `opacity(0.05)`, `allowsHitTesting(false)`.

Both reuse the existing hero shield asset, so nothing new lands for the palette
guard, and the list/tab panes are untouched (no watermark there, as the
reference shows).

## The subtitle — removed on the user's call

The reference has no subtitle below the pill; the app's was the backend's
`section.description`. It was surfaced as a keep-or-remove decision rather than
deleted on a guess — and the call came back **remove**, to match the reference.
Both platforms now go straight from the pill into the fields. Dropping it left
`summary` / `openSection` bound-but-unused, so those became plain null guards
(`if (state.openSection == null) return` / `if model.openSection != nil`).

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — `GloveboxViewModelTests` + `ScreenRenderTests` | **7 / 7 passed**, 0 failed |

Layout only; no test asserts the watermark. The on-device look is the user's to
confirm.

## Open

- None on this screen. The detail now matches the reference: title bar, pill,
  shield watermark, fields, upload well.