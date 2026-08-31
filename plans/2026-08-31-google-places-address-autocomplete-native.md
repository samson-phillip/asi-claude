# Scope — Google Places address autocomplete (native iOS + Android)

**Status:** scoping · **Date:** 2026-08-31 · **Parity source:** member-client
`addressAutocomplete.ts` + `googlePlaces.ts` (David feedback 2.11/2.12, #142).

This is the one item from the last member-client pull that can't be ported —
member-client uses the **Google Maps JavaScript API**, which doesn't run on
native. It has to be rebuilt on each platform's SDK. This scopes that.

---

## 1. What the feature does (behaviour to match)

On the address form: a **"Search Address"** field. As the member types (≥3
chars) it shows address predictions; selecting one **auto-populates Address
line 1, City, Postal code, Country and State/region**, and leaves every field
editable. **Address line 2 is never auto-filled** — the member types the
apt/suite/unit themselves (explicit in David's note).

**Degrade-to-manual is a hard requirement.** With no API key configured the
"Search Address" field is a plain text box and every address field stays
manually editable — exactly today's behaviour. Nothing breaks, nothing claims to
be searchable. member-client gates this on `placesEnabled()`; native mirrors it.

---

## 2. Architecture — shared pure core + thin native shim

member-client already splits this the right way, and it ports cleanly:

- **Pure, portable (port verbatim, unit-test):** `addressAutocomplete.ts` —
  `parseGooglePlace` (Google `address_components` → `{line1, city, postal,
  countryISO2, subdivisionName, subdivisionCode}`), `matchCountry`,
  `matchSubdivision`. All the decisions live here (the city fallback chain
  `locality → postal_town → sublocality → administrative_area_level_2`; line 1 =
  `street_number + route`; ISO-2-first country match). No SDK types leak in.
- **Thin, native (rewrite per platform):** `googlePlaces.ts` — the loader,
  predictions, and details calls. This is the only web-specific part.

The Google **Places SDKs return the same `types`-tagged address components** as
the JS API (`street_number`, `route`, `locality`, `postal_code`,
`administrative_area_level_1`, `country`), so the ported parser consumes them
directly on both platforms.

**Synergy already in place:** `matchCountry` keys on the country's `iso2`, which
the country-flags work just added to `Country`; subdivisions already carry a
`code`. So the "match the parsed result back to our master rows" half is ready.

---

## 3. Provider decision (the main call to make)

| | **A. Google Places SDK on both** (recommended) | **B. Apple MapKit on iOS + Google on Android** |
|---|---|---|
| Parity | Exact — same predictions, same component model, one mapper | Divergent — iOS results differ from web/Android |
| iOS key/cost | Needs a key; billed | **No key, no cost** on iOS |
| Mapper | One (`parseGooglePlace`) both platforms | Two — MapKit returns `CLPlacemark`, not `address_components`; needs a second parser |
| Precision | Address-typed predictions (`types: ["address"]`) | MapKit completer is POI-leaning; weaker for pure street entry |
| Data recipient | Google (both) | Apple (iOS) + Google (Android) — two processors to disclose |

**Recommendation: A — Google Places SDK on both.** It's the only option that
delivers real parity and lets one tested parser serve both apps. B saves the iOS
key/cost but buys a second code path, two mappers, and results that don't match
the web or Android — for a field members use once.

> If cost is the driver, the cheaper lever is **session tokens + field masking**
> (below), not a second provider.

---

## 4. API keys — none exist yet

Verified in member-client (2026-08-31) and confirmed here: **no Google Maps/Places
key is provisioned in any environment, and neither native app uses Places.** The
whole feature ships **behind a flag** and is dark until a key lands.

Native keys are **not** the web key — they're restricted differently:

- **iOS:** a key restricted to the **bundle id** (`com.app.attorney.shield`).
- **Android:** a key restricted to **package + signing-cert SHA-1** — so each
  signing key needs coverage (debug + the release key per track).
- **Per environment** (dev/uat/prod), same shape as the New Relic tokens →
  up to **6 keys**, wired per build variant (the dev/uat/prod branch model).

**Needs from Innocent / devops:** a Google Cloud project with **Places API +
Maps SDK for iOS/Android** enabled, **billing** attached, and platform-restricted
keys per environment. Keys are injected at build time (xcconfig / `local.properties`
/ CI secret) — **not committed** (same rule as the NR tokens).

---

## 5. Cost control (mirror the reference exactly)

- **Autocomplete session tokens.** One `AutocompleteSessionToken` per typing
  session, shared across every prediction request **and** the final
  fetch-details call, then discarded. Without it Google bills per keystroke
  (~18× a typing session); with it the whole search bills as one Place Details
  call. Both SDKs support this — mirror `endSession()` semantics.
- **Field masking.** Request only `addressComponents` (+ `formattedAddress`,
  `name`) on fetch — Places bills per requested field group.
- **`types: ["address"]`** on predictions, so a member typing a street doesn't
  get businesses whose name would land in line 1.

---

## 6. ⚠️ Data governance — a deliberate decision, not a default

Same class of decision we flagged for New Relic. Address autocomplete streams the
member's **partial typed address (PII), keystroke by keystroke, to Google** — in
an app built around legal encounters, PII, and documents. Before enabling:

- **Disclosure:** App Store **privacy labels** and Play **Data Safety** must
  declare the address text sent to a third party (and Apple's too, under option B).
- **Consent / jurisdiction:** GDPR/CCPA may require this be opt-in; the
  degrade-to-manual path is the natural "off" state.
- **Scope minimisation:** address-typed predictions only; no map, no location
  tracking, no storing predictions.

Degrade-to-manual means we can ship the form **now** and turn search on only once
governance signs off and a key exists — the flag decouples the two.

---

## 7. UI

A "Search Address" field above line 1. Typeahead (≥3 chars, debounced ~250ms) →
a predictions list → on tap, `fetchPlaceDetails` → parse → fill line1/city/postal,
select the matching country + subdivision, leave all editable. iOS: SwiftUI
overlay list; Android: Compose dropdown.

**Note on David 2.11 ("Label" → "Search Address"):** on mobile "Label" is the
address **nickname** ("Home", "Work"), not the search box — so this is an
**added** field, not a rename. The nickname stays.

---

## 8. Phasing

- **Phase 0 — pure core, now (no SDK, no key, no governance blocker):** port
  `parseGooglePlace` / `matchCountry` / `matchSubdivision` to Swift + Kotlin with
  the reference's real-payload tests (incl. the UK "no locality" case). Zero
  runtime risk; makes the hard part reviewable and done. **Can start immediately.**
- **Phase 1 — SDK + flag-gated UI:** add the Places SDK dependency, the
  autocomplete shim (session tokens, degrade path), and the "Search Address"
  field. Wired to read the key from build config; **with no key it's a plain text
  box**, so this can merge before keys exist.
- **Phase 2 — enable per environment:** keys land + governance signs off →
  flip on per env variant. No rebuild of logic, just config.

---

## 9. Effort (rough, once §3 + §4 + §6 are settled)

| | iOS | Android |
|---|---|---|
| Phase 0 (shared mapper + tests) | ~0.5 d (shared design; ~0.5 d total across both) | — |
| Phase 1 (SDK + shim + UI + degrade) | ~1–1.5 d | ~1–1.5 d |
| Phase 2 (enable) | config only | config only |

Small because the decision-heavy part is a straight port of an
already-designed, already-tested module.

---

## 10. Open decisions (need answers to start Phase 1)

1. **Provider:** Google Places SDK on both (recommended) vs MapKit-on-iOS?
2. **Keys:** Innocent to provision platform-restricted Places keys per env (Cloud
   project + billing + restrictions).
3. **Governance sign-off:** privacy-label / Data-Safety disclosure + consent
   posture for sending address text to Google.
4. **UX confirm:** "Search Address" as a new field above line 1; nickname "Label"
   stays.

Phase 0 needs **none** of these and can proceed on request.
