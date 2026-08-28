# 2026-08-28 — Profile & Personal Information brought to member-portal parity

## Task

The Account → "Profile & personal info" detail screen was a read-only card
(name + email). The CodePen has no spec for it, so — per the user's direction
("since codepen doesn't have it, lets do them like the member portal") — it was
rebuilt to match `member-client`'s two portal screens. Scope confirmed via
AskUserQuestion: **full parity, two screens** (an editable Profile editor plus a
new Personal Information screen), **avatar skipped for now**.

## Design authority

- `member-client` (Rank 3, behaviour) is the reference for these two screens,
  since neither the palette PDF nor the CodePen covers them. Colour still comes
  from the palette: gold CTAs with navy text, gold "+ Add" / action links, gold
  "Default" pill (navy text on gold), no unapproved colours.
- Mirrors `ProfileScreen.tsx` ("Edit Profile") and `PersonalInfoScreen.tsx`
  ("Personal Information") + `AccountScreen.tsx` (two rows: Profile,
  Personal Information).

## What shipped (both platforms, feature-for-feature)

**Edit profile**
- Ghost avatar (no camera badge — upload deferred).
- Full name (editable), Phone (editable), Email (read-only + hint "To change
  your email address, contact Support at support@attorney-shield.com").
- "Save changes" gated on a non-blank name; saves via `updateMyContactInfo`,
  then refreshes the session so Home's greeting updates.

**Personal information**
- Mailing addresses: list with map-pin, label + one-line summary, gold "Default"
  pill, and text actions (Set default / Edit / Remove); empty-state card; "+ Add".
- Add/Edit address sheet: Label, Address line 1 (required), line 2, City +
  Postal (grid), Country select, State/region select (only when the country has
  subdivisions), Default toggle. Save gated on line 1. Country change clears the
  stale state/region and reloads subdivisions.
- About you: Gender select ("Select gender"), Date of birth. "Save changes" via
  `updateMyProfile`.
- CRUD reloads the list from the server on success; refused delete/set-default
  never throw and keep the row (surfaced as an error, not a crash).

## Repos & files touched

- `kotlin`
  - `core/network/Models.kt` — `phoneE164` on `GqlUser`/`Me`; domain `Country`,
    `UserAddress` (+ `summary`), `AddressInput`; wire types for countries +
    address CRUD (`countryId`/`subdivisionId`, lowercase, per gateway).
  - `core/network/AsiApi.kt` — `phoneE164` in `getMe`; `updateMyContactInfo`,
    `listCountries`, `listUserAddresses`, `createUserAddress`,
    `updateUserAddress`, `deleteUserAddress`, `setDefaultUserAddress` (+
    `ADDR_FIELDS`, `addressInputJson`). List/lookup/delete/default never throw.
  - `feature/account/AccountViewModel.kt` — `AccountPane.PersonalInfo`,
    `AddressEditing`, `AddressForm`; profile/personal/address state + methods;
    `open()` loaders; `refreshContext()` after profile save.
  - `feature/account/AccountScreen.kt` — new `ProfilePane` (editor),
    `PersonalInfoPane`, `AddressCard`, `AddressSheet` (via `FloatingSheet`);
    overview split into Profile + Personal information rows; titles.
  - `MainActivity.kt` — wired the new `AccountCallbacks`.
  - `AccountViewModelTest.kt` — 8 new tests.
- `swift`
  - `Core/Network/Models.swift` — same domain + wire types; `phoneE164` on
    `GqlUser`/`Me`.
  - `Core/Network/AsiApi.swift` — same API surface (`Self.addrFields`,
    `addressInputJson`).
  - `Feature/Account/AccountViewModel.swift` — `.personalInfo` pane,
    `AddressEditing`, `AddressForm`; state + methods; `setAddressCountry` is
    `async` for deterministic tests.
  - `Feature/Account/AccountScreen.swift` — `profilePane` (editor),
    `personalInfoPane`, `addressCard`, `addressSheet` (native `.sheet` with
    `.presentationBackground`); overview split; titles. No new closures — the
    `@Bindable` model is called directly, as the other panes already do.
  - `AccountViewModelTests.swift` — 8 new tests.

## API endpoints used (existing gateway ops; none invented)

`updateMyContactInfo(input: UpdateMyContactInfoInput!)`, `countries`,
`userAddressList(userId)`, `createUserAddress`, `updateUserAddress`,
`deleteUserAddress`, `setDefaultUserAddress`, `subdivisionsByCountry`,
`updateMyProfile`, `userProfileByUser`, `user(id)` (+ `phoneE164`). Matches
`member-client/src/lib/memberApi.ts` + `profileApi.ts`.

## Test results

- **Android**: `:app:compileDebugKotlin` clean; `AccountViewModelTest`
  (existing + 8 new) — **all pass**. Installed and **verified live** on the
  Pixel 8a emulator (John Doe / salmson93@gmail.com): both Account rows present;
  Edit profile shows ghost avatar, seeded name, phone field, disabled email +
  support hint, gold Save; Personal information shows Mailing addresses empty
  state + "+ Add", About you (Gender/DOB), gold Save; Add-address sheet renders
  with Label/line1/line2/City+Postal/Default toggle, "Add address" correctly
  disabled until line 1 is filled.
- **iOS**: `xcodebuild build` — **BUILD SUCCEEDED**; `AccountViewModelTests`
  (existing + 8 new) — **all pass** (`xcodebuild test` exit 0).

## Notes / graceful degradation

- On this dev backend `countries` returns empty, so the Country/State selects
  hide (as designed) and the address sheet still works with the free-text
  fields. Same pattern as the empty incident-types / documents on this account.
- Date of birth is a text field (`YYYY-MM-DD`) matching the API's stored string,
  rather than a native date picker — kept simple and honest for parity.
- Avatar upload remains deferred (no camera badge shipped dead).
