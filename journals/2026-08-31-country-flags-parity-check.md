# 2026-08-31 — Country flags parity check

## Task

Fourth parity pass. member-client commits `7f42b26` ("Put a flag on every
country, and say where we think you are", #138) and `fb8f23d` ("Pin the flag's
code points", #139). Mirror the applicable part to the mobile apps.

## What the reference did

Two things:

1. **A flag on every country.** `countryFlag(iso2)` derives a flag emoji from the
   ISO-3166-1 alpha-2 code (🇰 + 🇪 regional indicators = 🇰🇪), so nothing is
   hard-coded, fetched, or shipped as ~250 SVGs — the OS draws flag emoji
   natively. Used in the **Current Location picker** (a list of every country) and
   the **Account row**.
2. **"Say where we think you are."** The Account Current-Location row names the
   place ("🇨🇦 Canada · ON — travelling") instead of describing itself.

## Mobile disposition

**Part 2 is N/A** — mobile has no Current Location feature or picker (confirmed in
the David pass). So there is no Current-Location picker or row to flag.

**Part 1 applies** to mobile's one country list: the **address country picker**
(Account → Personal information). Same UX the reference improved — a column of
country names behind no distinguishing mark — so the flag idea carries directly.

## What changed

- New pure helper `countryFlag(iso2)` on both platforms (`Core/Location/CountryFlag.swift`,
  `core/location/CountryFlag.kt`), a direct port of `countryFlag.ts`: ISO-2 → the
  regional-indicator pair; `""` for anything that is not two letters, so the caller
  falls back to a bare name rather than replacement boxes.
- `Country` gained an **`iso2`** field and a `flaggedName` computed accessor
  ("🇰🇪 Kenya", or the bare name when a master row has no code).
- The countries query now fetches it — `countries(limit: 300) { id iso2 name }`,
  matching the reference (the `iso2` field and the 300 limit are both from
  member-client's `listCountriesWithISO`; the limit stops a default page size
  truncating the list).
- The address country picker shows `flaggedName` for both the selected value and
  each option, on both platforms.

## Files

- Swift: new `Core/Location/CountryFlag.swift`; `Core/Network/Models.swift`
  (Country + GqlCountry), `Core/Network/AsiApi.swift` (query), `Feature/Account/AccountScreen.swift`
  (picker); new test `CountryFlagTests.swift`.
- Kotlin: new `core/location/CountryFlag.kt`; `core/network/Models.kt`,
  `core/network/AsiApi.kt`, `feature/account/AccountScreen.kt`; new test `CountryFlagTest.kt`.

## Tests

- Swift: `-only-testing:CountryFlagTests -only-testing:AccountViewModelTests`
  (single-process, iPhone 16 Pro) → **42 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `CountryFlagTest` + `AccountViewModelTest` → **BUILD SUCCESSFUL**.

Both flag tests pin the exact code points (not "two of something"), so an
off-by-one in the alphabet arithmetic fails rather than passing with a plausible
wrong flag — the point of the reference's #139 follow-up.

Committed to `dev` on both repos.

## Note

The flag rides on the `iso2` the gateway returns; a country whose master row has
no code degrades to the plain name, never a broken glyph. Remaining un-synced
theme from this member-client pull: **Google Places address autocomplete** (needs
native Places on each platform, not a port).
