# 2026-08-31 — Document icons (honour admin `icon`) + device-region fields

Two parts of Innocent's feedback item 6 ("admin document icons / country-varying
fields don't appear in the mobile app"), plus his Round Two note that the icons
are **Lucide names**, not URLs.

## A. Honour the admin `icon`

**Before:** both apps *ignored* `DocumentSection.icon` and picked a glyph from the
section `code`/`name` — "no image loader exists to honour it." member-client's
`IconValue` treats the value as, in order: an **image URL**, a **Lucide/Feather
name**, or a legacy emoji, with a built-in fallback.

**Now:** a pure `AsiIcons.sectionIcon(code, name, icon)` mirrors that resolution:

1. `http(s)` URL → load it (iOS `AsyncImage`), with the code glyph as fallback.
2. A known Lucide/Feather name → a local glyph.
3. Otherwise → the code/name glyph (unchanged behaviour).

Names are normalized (camelCase / snake_case / spaces → kebab) exactly like
member-client's `normalizeLucideName`.

Platform difference (inherent, documented):

- **iOS** maps a Lucide name → an **SF Symbol** (rich system set: `car.fill`,
  `heart.text.square.fill`, `shield.fill`, `globe`, …) and renders **URL** icons
  natively via `AsyncImage`.
- **Android** has no symbol font and no image loader wired, so a Lucide name maps
  to the **nearest of the four bundled section glyphs**, and a **URL** icon shows
  the code glyph (its `Remote.fallbackRes`) until Coil is added. The resolution
  *logic* and the name normalization are identical; only the glyph vocabulary and
  URL rendering differ.

**Follow-up for Android parity:** add `io.coil-kt:coil-compose` so `Remote` URL
icons render (one composable change; the resolver already yields `Remote(url,
fallback)`).

## B. Fields carry the device region

member-client passes the member's **effective country** (device time zone, else
home) to `adminDocumentFieldList(countryISO2:)` — fields like `state_of_issue`
vary by country. The document **types** list is global (no country arg), and I
kept it that way to match.

**Now:** `listDocumentFields` takes `countryISO2` and the Glovebox passes
`TimeZoneCountry.current()` (the same device region already sent as the call's
`currentCountry`). Null → the gateway's global set, exactly as the web client's
`code || null`.

## Files

- Swift: `Core/Design/AsiIcons.swift` (`SectionIcon` + `sectionIcon` + Lucide→SF
  Symbol map), `Feature/Glovebox/GloveboxScreen.swift` (`SectionGlyph`),
  `Core/Network/AsiApi.swift` (`listDocumentFields(countryISO2:)`),
  `Feature/Glovebox/GloveboxViewModel.swift`; tests `AsiIconsTests.swift`,
  `GloveboxViewModelTests.swift`.
- Kotlin: `core/design/AsiIcons.kt` (`SectionIcon` + `sectionIcon` + Lucide→
  drawable map), `feature/glovebox/GloveboxScreen.kt`, `core/network/AsiApi.kt`,
  `feature/glovebox/GloveboxViewModel.kt`; tests `AsiIconsTest.kt`,
  `GloveboxViewModelTest.kt`.

## Tests

Resolver (both platforms): a Lucide name resolves to a glyph (with normalization);
an `http(s)` icon is `Remote` carrying the code fallback; an absent/unknown/emoji
icon falls back to the code glyph. Country plumbing (both): the fields query asks
for `countryISO2: $country` and sends the upper-cased value, or null when unknown.

- Swift: `AsiIconsTests` + `GloveboxViewModelTests` (single-process, iPhone 16
  Pro) → **35 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `AsiIconsTest` + `GloveboxViewModelTest` → **BUILD SUCCESSFUL**.

## For Innocent (confirm)

- Document-type `icon` values: are they Lucide names (`car`, `id-card`, `shield`,
  `globe`) and/or image URLs? We honour both; a bare emoji falls back to our glyph.
- We send `countryISO2` (device region) on `adminDocumentFieldList`, like
  member-client. Confirm the arg name is `countryISO2` on the gateway (it is in
  the web client).
