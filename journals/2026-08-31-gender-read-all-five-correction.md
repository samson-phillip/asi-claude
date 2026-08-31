# 2026-08-31 — Gender: display all five on read (correcting the tidy)

## What was wrong

The earlier "gender tidy" (per Innocent's 07-28 note) narrowed the picker to
Male/Female/Other — correct for **input** — but I also **dropped `non_binary`
from the enum** and made the picker resolve its displayed value by index into the
three options. Innocent's backend review caught the consequence: on dev **52 of 70
profiles hold `unspecified` (50) or `non_binary` (2)** — values the picker no
longer offered — so those profiles would render a **blank** gender field. Dropping
a value the member actually set is worse than showing it.

His guidance: keep the five-value enum, keep the three-option picker for input,
and map the other two to a read-only display. Nothing changes on the backend.

## Fix

Kept the **full five-value** `Gender` enum (restored `non_binary`) so every value
still decodes with a label. The three offered for **input** live in a
`Gender.selectable` list the pickers use. The stored value is displayed on
**read** regardless of whether it's selectable:

- **Enum** (both platforms): `non_binary` restored; `selectable = [male, female,
  other]` for the pickers; `fromWire` still decodes all five.
- **Account** (both platforms): stores the real `Gender?` (was an index into the
  three options — which is why non-selectable values blanked). `genderLabel` shows
  the real label (incl. "Non-binary"); `unspecified` maps to the placeholder, not
  "Prefer not to say". Picking one of the three replaces it; an untouched
  `non_binary` **round-trips unchanged** on save (no silent data loss).
- **Setup** (both platforms): already stored `gender: Gender?` and displayed its
  label; only its picker options/select moved to `selectable`.

## Files

- Swift: `Core/Network/Models.swift`; `Feature/Setup/SetupScreen.swift` +
  `SetupViewModel.swift`; `Feature/Account/AccountScreen.swift` +
  `AccountViewModel.swift`; tests `SetupViewModelTests.swift`,
  `AccountViewModelTests.swift`.
- Kotlin: `core/network/Models.kt`; `feature/account/AccountViewModel.kt`; tests
  `AccountViewModelTest.kt` (+ `SetupViewModelTest.kt` already used `selectable`).

## Tests

Added a regression guard on each platform — `aNonSelectableGenderStillDisplaysOnRead`
/ `a non-selectable gender still displays on read`: `non_binary` →
"Non-binary", `unspecified` → placeholder (null), `male` → "Male".

- Swift: `AccountViewModelTests` + `SetupViewModelTests` → **81 tests passed**.
- Kotlin: `AccountViewModelTest` + `SetupViewModelTest` → **BUILD SUCCESSFUL**.

## Note

This is item #6 of Innocent's answers to the mobile questions
(`notes/innocent-six-asks-response.md` context). Writing Male/Female/Other was
always fine; reading needed all five. The enum is deliberately **not** narrowed —
narrowing it is a schema change + migration + a business decision on the two
`non_binary` rows, not a picker change.
