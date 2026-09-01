# 2026-09-01 — Wheel date picker for date of birth (Personal information)

## Task

On the Personal information screen (33C), the **Date of birth** field was a plain
text field with a `YYYY-MM-DD` placeholder — easy to mistype and no calendar
help. Replace it with a **wheel date picker**. member-client uses a native
`<input type="date">` (a wheel on mobile), so a native wheel is the parity match.

## Design

The field becomes a **tappable row** (styled like the gender select, showing the
chosen date as "4 Jul 1990" or "Select date") that opens the wheel — the member
scrolls to a date instead of typing one. The stored/sent value stays the ISO
`YYYY-MM-DD` string `updateMyProfile` expects, so nothing downstream changes.

## Shared, pure, tested

`BirthDate` on both platforms — the bridge between the ISO string and the wheel's
components: `parse(YYYY-MM-DD)` (rejects non-dates like Feb 30 / month 13),
`iso` (zero-padded), `daysInMonth` (leap-year correct: 1900 not leap, 2000 leap),
`clampDay` (Jan 31 → Feb 28/29). Kept out of the view so the round-trip is
unit-tested without a picker.

## Platforms

- **iOS** (`AccountScreen.swift`) — a `.sheet` with a
  `DatePicker(.wheel)` bound to the stored ISO via `BirthDate` (a UTC calendar so
  no time-zone day-drift), range **1900…today** (no future), Done to close. The
  row shows a medium-format date.
- **Android** (`AccountScreen.kt`) — a `FloatingSheet` with three
  `NumberPicker` wheels (Year / Month-names / Day) via `AndroidView`. The **day
  count follows the chosen month/year** (`daysInMonth`), year caps at the current
  year, and Done writes `BirthDate(...).iso`. The pickers are wrapped in a dark
  `ContextThemeWrapper` so their numbers stay light on the navy sheet
  (`NumberPicker` takes its text colour from the platform theme, not Compose) —
  and `displayedValues` is cleared before shrinking a wheel's range so a shorter
  month can't index a stale label array.

## Files

- Swift: `Core/Format/BirthDate.swift`, `Feature/Account/AccountScreen.swift`;
  test `BirthDateTests.swift`.
- Kotlin: `core/format/BirthDate.kt`, `feature/account/AccountScreen.kt`; test
  `BirthDateTest.kt`.

## Tests

`BirthDate` (both platforms): parses a valid ISO date, rejects non-dates, formats
zero-padded, round-trips, counts leap/non-leap February and 30/31-day months,
clamps a day into its month. The wheel UI itself (SwiftUI `DatePicker` /
`NumberPicker`) is platform-native and not unit-tested; the value round-trip that
feeds it is.

- Swift: `BirthDateTests` (single-process, iPhone 16 Pro) → **6 passed**,
  `** TEST SUCCEEDED **` (app compiles with the new field).
- Kotlin: `BirthDateTest` → **BUILD SUCCESSFUL**; full `assembleDebug` green.
