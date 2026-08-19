# 2026-08-19 — Section detail: the upload control as the reference's well

## Task

Bring the Glovebox **section-detail** screen (14D, "Citizenship Info", reached by
tapping a section) toward the CodePen. Repos touched: `kotlin`, `swift`,
`asi-claude`.

## What the screen actually is — and what the reference is asking for

The detail pane renders whatever fields the backend defines for the section
(`adminDocumentFieldList`), through a `FieldRow` that already handles text,
dropdown and file kinds. For **Citizenship** the backend defines **two file
fields** — "Passport" and "Birth Certificate or Visa" — and nothing else.

The CodePen mockup shows far more: a masked **Passport number**, an **Issued in**
dropdown, a **Visa number**, an **Additional information** field, an uploaded
`passport-photo-page.jpg` tile, and **Camera / Gallery** buttons. Almost all of
that is **not stylable from the client**:

- **The four structured fields don't exist in the data.** The app renders the
  fields the backend returns; it can't invent Passport-number / Issued-in /
  Visa-number / Additional-information fields the section was never configured
  with. If the backend adds them (as text/dropdown), `FieldRow` already draws
  them. Recorded as a backend field-config gap.
- **The uploaded document is data**, not styling — the member here has uploaded
  nothing, so the fields are empty.
- **Camera / Gallery stays out.** The documented, repeated decision: nothing
  captures from the camera, and the single picker already offers gallery and
  files, so a Camera button would open the same picker under a false label.

## What was fixable — the upload control

The one clear, honest, palette-safe gap: the empty file field rendered a thin
one-line "+ Upload a document", where the reference draws a **larger dashed
well** — a cloud, "Upload document", and a hint. Rebuilt `AddDocumentControl` to
the reference's **two states**:

- **Empty** → the well: a cloud glyph, "Upload document", "PDF or a photo".
- **Has documents** → the compact "+ Add another document" beneath the tiles,
  unchanged.

That is exactly how the mockup treats "Birth certificate" (empty well) versus
"Passport" (a tile plus the compact add). Icons: Android uses the existing
`ic_tool_cloud`; iOS uses the `icloud.and.arrow.up` SF Symbol (no cloud imageset
exists, and the app already draws SF Symbols elsewhere), so nothing new lands in
a `.swift` file for the palette guard.

## Left as-is, deliberately

- **"Save changes"** stays. It commits text/dropdown values; on a file-only
  section it sits disabled, which is correct, not a bug.

## Addendum — the detail title bar (superseding the header note)

The header was first left alone; on request it now matches the reference. The
section-detail pane (14A-14D) takes a proper **title bar**: a back chevron on the
left with the section name **centred**, replacing the left "Back" text and the
big left-aligned title that sat in the body.

- Kotlin — a `DetailTitleBar` composable; the chevron is the `‹` glyph, matching
  how `AsiNavRow` already draws its `›` as text rather than shipping a drawable.
- iOS — a `detailTitleBar` with the `chevron.left` SF Symbol, the same way the
  app already uses `chevron.down` elsewhere.

No new asset on either platform, so nothing lands for the palette guard. The list
panes (tab 31, checklist 14) are untouched — they still open on their own title
with no bar, which is what the reference shows for them. The title is centred and
held clear of the chevron on both sides, and ellipsises if a section name is very
long.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — `GloveboxViewModelTests` + `ScreenRenderTests` | **7 / 7 passed**, 0 failed |

Layout-only; no test asserts the upload control's shape. The on-device look is
the user's to confirm on the signed-in emulator, which the suites sign out.

## Open

1. **Backend field config for Citizenship** — the structured fields the mockup
   shows (passport number, issued-in, visa number, additional info) need to be
   defined server-side before the app can render them.
2. The section-detail **header** treatment, if the centred-title/chevron form is
   wanted app-wide (would need a chevron asset).