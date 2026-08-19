# 2026-08-19 — Payment & plan (33A) to the design

## Task

Bring the Payment & plan screen (33A, reached from Profile) to the CodePen. No
screenshot supplied, so worked from `code_pen_design.html` (~13185-13236) plus the
code. Three choices were put to the user first, because each touches a deliberate
prior decision. Repos touched: `kotlin`, `swift`, `asi-claude`.

## Decisions taken (by the user)

1. **Plan card → compact**, matching the reference (was a deliberate line-item
   breakdown).
2. **Delete account → Live Red tint** (was a neutral outlined control, because the
   palette names no danger colour).
3. **Title bar on all Account sub-panes** (the header is shared, so it was this or
   an inconsistent one-off).

## What changed

### Title bar (all Account sub-panes)

The shared sub-pane header was the brand lockup + a text "Back". It is now the
reference's title bar (33A-33D): a back chevron on the left with the pane title
**centred** — `DetailTitleBar` / `detailTitleBar`, the same shape as the Glovebox
detail, chevron as the `‹` glyph on Android and the `chevron.left` SF Symbol on
iOS. A per-pane title map (`accountPaneTitle`) feeds it, and the big in-body title
was removed from every sub-pane (Profile, Plan, Family, Settings, Billing,
Legal, Delete account). The brand lockup is gone from the sub-panes, which also
settles the "brand sits on Home" point for this screen. Back behaviour is
unchanged (`backToOverview`), so nothing regresses — including Legal's nested
open-document view, which keeps its own in-body title and "Back to documents".

### Plan card → compact

Was plan name + status + a per-line itemisation + a Total row. Now the
reference's summary: a gold plan eyebrow, the member composition ("You + N
members") as the headline, the **rate in gold** on the right, then "Renews … ·
● Covered". Coverage stays a green *fill* dot with the word in legible text (R4),
never green text. The per-line "what am I charged for" detail is dropped, per the
decision — worth remembering it was originally deliberate.

### Delete account → Live Red

The reference's one red action. Rendered with Live Red — the palette's single
red, already used as a tint on the document-remove control — as a faint fill, a
border, and a bold label. Not a new colour: `AsiPalette.LiveRed` / `.liveRed`,
used at bold weight so the label clears the 3:1 bar for a large UI control.

### Also

"Plan changes are not available in the app." text removed — the reference conveys
it by simply having no Change-plan row, and the annotation confirms that intent.

## Left as-is

- **Payment method has no "Update"** — there is still no `updatePaymentMethod`
  API (B7 in backend-asks); the row shows the card without a control that would
  always fail. The reference's "Update ›" needs the backend first.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — `AccountViewModelTests` | **8 / 8 passed**, 0 failed |

Layout-only against the view models; no test asserts this screen's geometry. The
on-device look is the user's to confirm. Notable: the compact card's gold price
is `formatRate(...)` ("$46.00/mo" or "$228 every 6 months"), which is honest
about cadence — the reference's separate "$/mo" figure would need a per-month
derivation the billing data doesn't reliably give.

## Open

- **Payment method "Update"** — blocked on the backend (B7).
- The title-bar change touched all Account sub-panes; worth an eye on Family /
  Settings / Billing / Legal / Delete-account, not just Payment & plan.