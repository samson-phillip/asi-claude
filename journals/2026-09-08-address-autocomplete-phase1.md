# 2026-09-08 — Address search autocomplete, Phase 1 (both platforms)

Built **Phase 1** of the Google Places address autocomplete on the personal-info
mailing-address form (both apps), per
`plans/2026-08-31-google-places-address-autocomplete-native.md`. Phase 0 (the pure
`parseGooglePlace` / `matchCountry` / `matchSubdivision` parser) was already done and
tested; this adds the network layer + the "Search Address" UI + the wiring.

## Decision the user made

"Client-direct Google Places, key from config." So the app calls Google directly
with a key read from app config; degrades to today's manual form when no key is set.

## One deliberate deviation from the plan: REST, not the SDK

The plan (§3) recommended the native **Places SDK**. I used the Places **Web
Service REST** (client-direct HTTPS to `maps.googleapis.com`) instead, because:
- it consumes the exact `address_components` model the tested parser already expects
  (one mapper, verbatim), and
- it is **fully unit-testable with stubbed HTTP** (MockWebServer / StubURLProtocol) —
  the SDK can't be, so I could build + verify everything now without a real key.
Same provider, same component model, session tokens + field masking as query params;
no heavy native dependency. Noted here as the SDK→REST call.

## Behaviour (matches member-client + the plan)

- A **"Search Address" field above line 1**, shown only when a key is configured.
  The **"Label" nickname field stays** (plan §7 — it is NOT the search box).
- Typing (≥3 chars, ~300ms debounce) → address-typed predictions → pick →
  `placeDetails` → `parseGooglePlace` → fills **line 1 / city / postal / country /
  subdivision**, leaving all editable. **Line 2 is never auto-filled.**
- **Degrade-to-manual is hard-gated on key presence** (`placesEnabled`): no key →
  no search field, fully manual form, exactly today. Any Places failure is
  swallowed (empty/nil) so the form never breaks.
- **Cost control:** one session token per typing session, shared across predictions
  and the details call then discarded; `types=address`; `fields` masked to the
  components (plan §5).

## Ships dark — still needs a key + governance

No key is provisioned, so this is **live but dark**. Turning it on (Phase 2) needs
(a) platform-restricted Places keys per env from Innocent/devops, wired into build
config (`BuildConfig` / xcconfig → Info.plist, never committed), and (b) the
privacy-label / Data-Safety governance sign-off for sending typed address text to
Google (plan §6). The degrade-to-manual gate decouples shipping from enabling.

## What changed

- **Config:** `AsiConfig.placesApiKey` (nil default) + `placesBaseUrl` (injectable
  for tests).
- **API:** `AsiApi.placesEnabled`, `placeAutocomplete(query:sessionToken:)`,
  `placeDetails(placeId:sessionToken:)` (best-effort; GET to the Places web service)
  + snake_case wire DTOs mapped to the pure `GooglePlace`. `AddressPrediction` type.
- **AccountViewModel:** `addressSearchEnabled` / `addressSearchQuery` /
  `addressPredictions` / `addressSearching`, a debounced `onAddressSearchChange`,
  `pickAddressPrediction` (details → parse → match country + load/match subdivision →
  fill), a per-session token, reset on open/close.
- **AccountScreen:** the "Search Address" field + predictions dropdown on the
  address sheet, gated on `addressSearchEnabled`; callbacks wired through
  `MainActivity` (Android). iOS uses a `Binding` onto `onAddressSearchChange`.

## Tests

- **Android** (`:app:testDebugUnitTest` green): `AsiApiTest` +6 (placesEnabled;
  autocomplete parse + `types=address`/token/key on the query; no-key → no request;
  failure → empty; details → parseable place; no-key → null). `AccountViewModelTest`
  +3 (off without key; <3 chars → no lookup; type → predictions → pick fills
  line1/city/postal, not line2, dropdown clears). Parser tests already existed.
- **iOS** (`AttorneyShieldTests`): the same set mirrored across `AsiApiTests` +
  `AccountViewModelTests` (instant `addressDebounce` injected; `waitUntil` polls the
  fire-and-forget search Task). Existing `AddressAutocompleteTests` cover the parser.

## Files

- Kotlin: `core/network/AsiConfig.kt`, `core/network/AsiApi.kt`,
  `core/network/Models.kt`, `core/location/AddressAutocomplete.kt`,
  `feature/account/AccountViewModel.kt`, `feature/account/AccountScreen.kt`,
  `MainActivity.kt`; tests `AsiApiTest`, `AccountViewModelTest`.
- Swift: `Core/Network/AsiConfig.swift`, `Core/Network/AsiApi.swift`,
  `Core/Network/Models.swift`, `Core/Location/AddressAutocomplete.swift`,
  `Feature/Account/AccountViewModel.swift`, `Feature/Account/AccountScreen.swift`;
  tests `AsiApiTests`, `AccountViewModelTests`.
