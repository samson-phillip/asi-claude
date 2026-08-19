# 2026-08-19 — Glovebox section icons: three of four were a generic folder

## Task

Reported against a device screenshot: the Glovebox "doesn't look like the
CodePen." Repos touched: `kotlin`, `swift`, `asi-claude`.

## Two things the screenshot clarified before any fix

**The screenshot was screen 31 (the Glovebox _tab_), not screen 14.** The
mockup supplied earlier was screen 14, "Upload documents" — the checklist step,
with the "Finish your profile" eyebrow, the "Mark documents as complete"
checkbox and the gold "Done — back to checklist" button. The screenshot is the
tab reached from the bottom bar: "Digital Glovebox", "Secured · shareable…", no
checkbox, no Done button. Both are correct for what they are, and they share the
same row component (`SectionRow` / `SectionGlyph`), which is where the real fault
was.

**Colour was ruled on, not changed.** The CodePen draws the icon tiles and the
View/Add links in steel blue `#2E78C8`; the app renders them gold because
`design/color-system.md` (Rank 1) rules that blue out. Asked, the decision was
to **keep gold**. So no palette change — the deviation stays documented and
intentional.

## The real defect — icon lookup keyed on `code` alone

Three of the four rows (Driver's, Gun, Health) drew the generic folder
(`ic_section_other`); only Citizenship drew its real glyph.

`SectionGlyph` resolved the glyph with `AsiIcons.section(code.ifBlank { name })`
— i.e. the display **name** was used only when `code` was *blank*. But `code`
is never blank; it is whatever `adminDocumentTypeList.code` returns, and the
live gateway's codes for driver/gun/health are **not** the snake_case of their
names, so the lookup missed and fell through to the generic glyph. Citizenship's
code happened to normalize to a key we had (`citizenship_info`), which is why it
alone was right — and why the bug looked like "one works, three don't" rather
than "all wrong."

The display names, by contrast, all normalize cleanly onto keys we already have
(`drivers_information`, `gun_information`, `health_information`,
`citizenship_info`). So the name is the reliable key here, not the code.

### The fix

`AsiIcons.section(code, name)` now tries the code, then the name, then the
generic glyph. One call site on each platform. Mirrored on `kotlin` and `swift`.

The generic fallback is unchanged, so a section the app has never been taught
still shows the neutral folder rather than a wrong glyph.

## Why it shipped: `section()` had no test

`AsiIconsTest` / `AsiIconsTests` covered `incident()` in exactly this scenario —
"the codes the gateway actually returns resolve" — but never `section()`. The
section map was written on the same assumption and never exercised against the
real wire shape, so the identical bug that was caught for incident tiles went
unnoticed for Glovebox sections. Added section regression tests on both
platforms: resolves-by-name-when-code-misses, matching-code-wins, and
unknown-falls-back-distinctly.

## Not changed, on purpose

- **Row order.** The app shows the four alphabetically (Citizenship, Driver's,
  Gun, Health) because `listDocumentSections` sorts by `sortOrder` then name and
  the gateway returns them with equal sort order. The CodePen's order (Driver's,
  Health, Gun, Citizenship) is the mock's own `sortOrder`. Order is backend data,
  not a client concern — left alone.
- **"attorney" vs "Law Firm Representative".** The tab's subtitle says "your
  attorney"; the CodePen says "Law Firm Representative". This is the same
  app-wide wording decision left open on 2026-08-19 (screen 14) and is not
  resolved here.

## Verification

- Android unit — `AsiIconsTest`, including the three new section tests: **pass**
  (`BUILD SUCCESSFUL`, source compiles clean bar two pre-existing deprecation
  warnings).
- iOS unit — `AsiIconsTests`, all 7 (incl. the three new section tests):
  **`TEST SUCCEEDED`**.

The screenshot came from a **signed-in Android session**, which the test suites
sign out (per the standing constraint). So the on-screen confirmation — the
Glovebox rows now drawing a car, a shield-with-cross and a target instead of
folders — is the user's to make on their live emulator; the logic is locked by
the unit tests.

## Open

1. **The real live section codes are still unknown.** The name-fallback is the
   safety net; if the codes are ever captured they should be added to
   `bySectionCode` so the mapping survives a localized/renamed display name.
2. **"attorney" vs "Law Firm Representative"** on the Glovebox tab — pending.
