# 2026-08-31 — Google Places Phase 0: the pure address mapper

## Task

Phase 0 of the native Google Places feature scoped in
`plans/2026-08-31-google-places-address-autocomplete-native.md`: port the pure,
decision-heavy core (`parseGooglePlace` / `matchCountry` / `matchSubdivision` /
`isUsableAddress`) from member-client's `addressAutocomplete.ts` to Swift +
Kotlin, with the reference's real-payload tests. **No SDK, no API key, no
governance blocker** — this is the part that can be done and reviewed now while
the provider/keys/governance decisions happen in parallel.

## What was ported

`GoogleAddressComponent` / `GooglePlace` / `ParsedAddress` value types plus:

- **`parseGooglePlace`** — Google `address_components` → `{addressLine1, city,
  postalCode, countryISO2, subdivisionName, subdivisionCode}`. Carries the
  reference's two non-obvious decisions verbatim:
  - **City fallback chain** `locality → postal_town → sublocality_level_1 →
    sublocality → administrative_area_level_2`, so City is not left empty on a UK
    (postal_town) or dense-urban (sublocality) address the member just watched
    populate everything else.
  - **Line 1** = `street_number + route`, then `premise` (named building), then
    the place `name`. **Address line 2 is never produced** — the type has no such
    field, so a `subpremise` is dropped (the member types the apt/suite).
- **`matchCountry`** — ISO-2 first (Google "United States" vs master "United
  States of America"), name only as a fallback for a master with a blank iso2,
  else nil. Uses the `iso2` the country-flags pass just added to `Country`.
- **`matchSubdivision`** — full name first, then code, both compared against the
  master's `name` (masters are inconsistent about which they store).

## Files

- Swift: `Core/Location/AddressAutocomplete.swift`; test `AddressAutocompleteTests.swift`.
- Kotlin: `core/location/AddressAutocomplete.kt`; test `AddressAutocompleteTest.kt`.

Operates on the real `Country` / `Subdivision` models (both already carry the
fields the matchers need), so Phase 1 can wire the parsed result straight into
the address form.

## Tests

Every case from member-client's `addressAutocomplete.test.ts` mirrored, incl. the
US common case and the **UK "no locality"** shape:

- Swift: `-only-testing:AddressAutocompleteTests` (single-process, iPhone 16 Pro)
  → **13 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `AddressAutocompleteTest` → **BUILD SUCCESSFUL**.

## Next (still gated on decisions from the scope doc)

Phase 1 — the Places **SDK shim** (predictions/details + session tokens),
flag-gated so no key ⇒ plain text field — needs the provider decision (Google
SDK on both, recommended), platform-restricted keys per env from Innocent, and
the data-governance sign-off. The mapper this journal covers is the part that
needed none of them.
