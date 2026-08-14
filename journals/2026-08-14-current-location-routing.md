# 2026-08-14 — Current-country routing (`currentCountry`), both apps

## Task

Backend write-up item 4 (`2026-08-14c-member-context-dev-defaults.md`): neither
native app tells comms where the member **currently is**, so a member arrested
two states from home reaches an attorney licensed where they *live*, not where
they *are*. Send `currentCountry` on `member-call` so routing can prefer the
current location, falling back to the profile country server-side.

## The one real decision: time zone, not GPS, not locale

`currentCountry` is derived from the **device time zone**, deliberately:

- **Not GPS / reverse-geocode.** The Android location provider avoids Google on
  purpose (works on de-Googled devices), and reverse-geocoding needs Play
  Services. Geocoding also returns country *names*, not ISO codes, and needs a
  network round-trip and a location permission — none of which a call placement
  should wait on.
- **Not the locale.** The locale follows the phone's *language*, not where it
  physically is — a US traveller with an `en_GB` phone is in the US.
- **The time zone is right.** It is offline, permission-free, instant, works
  de-Googled, and moves with the phone. `America/New_York` → `US`.

Server-side this is a *hint*: comms still falls back to the profile country, so
an unknown/unmapped zone must be **omitted**, never sent blank.

**Subdivision (`currentSubdivision`) is not sent in v1.** The contract wants ISO
subdivision codes; the time zone only yields a country, and reverse-geocoding
yields names not codes. Left as a documented follow-up rather than sending a
wrong or made-up value.

## What each platform uses for the tz→country map

- **Android** — ICU already ships it: `android.icu.util.TimeZone.getRegion(id)`.
  New `core/location/TimeZoneCountry.kt` wraps it, filtering ICU's `"001"`
  (world) sentinel down to a genuine two-letter code. No table to maintain.
- **iOS** — Foundation exposes no tz→country API, so
  `Core/Location/TimeZoneCountry.swift` carries a **418-entry table generated
  from the tz database's `zone.tab`**. Same public shape as Android
  (`country(for:)`, `current(_:)`).

## Wiring

`StartCallArgs` gained `currentCountry: String?` on both platforms. The
`member-call` body **omits it when nil/blank** — same conditional-put pattern
already used for `jurisdictionId`. `CallViewModel` takes an injected
`currentCountry` provider defaulting to `TimeZoneCountry.current()`; the two
production call sites (`MainActivity.kt`, `AttorneyShieldApp.swift`) pass nothing
and so use the real device time zone. Injecting the provider is what makes the
send/omit behaviour unit-testable without depending on the test machine's zone.

## Files

- **kotlin**: `core/location/TimeZoneCountry.kt` (new), `core/network/Models.kt`
  (`StartCallArgs.currentCountry`), `core/network/AsiApi.kt` (conditional body),
  `feature/call/CallViewModel.kt` (injected provider + default).
- **swift**: `Core/Location/TimeZoneCountry.swift` (new, 418-entry map),
  `Core/Network/Models.swift`, `Core/Network/AsiApi.swift`,
  `Feature/Call/CallViewModel.swift`.

## API

`POST {API_BASE_URL}/api/vonage/video/member-call` — added optional
`currentCountry` (ISO alpha-2). No new endpoint; no other field changed.

## Tests

**Android 429 / 0** (was 427, +2), **iOS 410 / 0** (was 405, +5/6 new):

- Call body **includes** `currentCountry` when the provider resolves one (`US`).
- Call body **omits** `currentCountry` when the provider returns nil — comms
  falls back to the profile country; never a blank string.
- iOS `TimeZoneCountryTests`: known zones map correctly
  (`America/New_York`→US, `Africa/Nairobi`→KE, `Europe/London`→GB,
  `Europe/Paris`→FR via `current(_:)`), an unknown/empty zone is nil, and
  **every** one of the 418 values is a valid upper-case alpha-2 code.

### Note on Android map coverage

The tz→country mapping on Android is the platform's own ICU, not our code, so it
is not unit-tested in plain JUnit (`android.icu` throws "not mocked" there, and
the project has no Robolectric). The wiring is covered by the CallViewModel
tests; the mapping itself is authoritative ICU and was exercised live on the
Infinix during the earlier two-way-video runs. The **iOS** table — the part we
hand-generated and could get wrong — is fully unit-tested.

## Open issues / next steps

- **`currentSubdivision`** — deferred (ISO subdivision codes not obtainable from
  the time zone; reverse-geocode gives names). Revisit if the backend needs
  state-level routing and can accept names or a profile-side lookup.
- Worth a live check next device session: place a call and confirm comms logs
  the `currentCountry` it received.
