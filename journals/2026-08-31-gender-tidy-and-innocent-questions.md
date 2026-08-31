# 2026-08-31 — Gender options tidy + questions for Innocent

Two small deliverables off Innocent's 2026-07-28 platform feedback (see
`notes/innocent-platform-feedback-mobile-triage.md`).

## 1. Gender tidy — Male / Female / Other

The doc (II, Gender Options): hardcode gender to Male / Female / Other. The apps
already hardcoded gender, but the picker offered five options (Male, Female,
Non-binary, Other, "Prefer not to say").

Reduced the picker to the three the product offers, keeping an `unspecified` value
as the not-set default and wire fallback (so a fresh profile and any legacy/unknown
gateway value still resolve cleanly):

- **Swift** — `Gender` drops `nonBinary`; `allCases` is overridden to
  `[.male, .female, .other]`, so every gender picker AND its index resolution share
  one canonical list with no call-site changes. `unspecified` stays a raw value.
- **Kotlin** — `Gender` drops `NON_BINARY`; added `Gender.selectable =
  [MALE, FEMALE, OTHER]` and pointed the pickers/index sites at it (Setup + Account
  screens/VMs). `entries` (incl. `UNSPECIFIED`) still backs `fromWire`.

Tests updated (both selected Non-binary before): now select Other and assert the
`other` wire value.

- Swift: `SetupViewModelTests` + `AccountViewModelTests` → **81 tests passed**.
- Kotlin: `SetupViewModelTest` + `AccountViewModelTest` → **BUILD SUCCESSFUL**.

Note: "subject to language translation" is **not** done — the native apps have no
UI-localisation layer (all copy is English); translating gender labels alone would
need an app-wide i18n decision. Flagged to Innocent, not built.

## 2. Questions for Innocent

`notes/mobile-questions-for-innocent-from-platform-feedback.md` — the mobile-side
questions the native apps need answered before building the new behaviour:
Sanctions call-block field, Financial Status field, the authoritative
trial-converted signal (cross-refs the trial write-up), connecting-screen message
delivery (comms per-call vs static config), the documents order/field API + native
vs web, and confirmation the gateway `Gender` enum standardises on
male/female/other. Each says what the app will do with the answer.

## Files

- Swift: `Core/Network/Models.swift`, `AttorneyShieldTests/SetupViewModelTests.swift`.
- Kotlin: `core/network/Models.kt`, `feature/setup/SetupScreen.kt` + `SetupViewModel.kt`,
  `feature/account/AccountScreen.kt` + `AccountViewModel.kt`, `SetupViewModelTest.kt`.
- asi-claude: the two notes above + this journal.
