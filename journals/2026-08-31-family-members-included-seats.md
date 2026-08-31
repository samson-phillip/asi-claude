# 2026-08-31 — Family members: included seats are addable without a seat price

## Report

On the Family members screen (33B) a member with *"0 of 2 sub-accounts added …
Included in your plan"* saw *"This plan has no seat price configured, so members
cannot be added,"* with **no Invite action** — they could never fill their own
included family spots.

## Root cause

The app required a `seatPriceId` to add **any** sub-account. It derived that from a
second membership line (the "seat line"); a plan whose members are *included*
(free) has no such line, so `seatPriceId` was nil → `canAddMember` false → the
Invite action was hidden and the add was blocked.

That contradicts the reference. member-client (`AddSubaccountScreen.tsx`) requires
a seat price **only for *additional* (beyond-included) seats** — an **included**
sub-account is added with **no** `seatPriceID` at all (`addSubaccount({org,
firstName, lastName, email})`). And the app only ever surfaces *included* spots
(`openSeats` is capped at `includedSubaccounts`), so none of them needed a price.

## Fix (both platforms)

- **API `addFamilyMember`**: `seatPriceId` is now optional and included in the
  payload only when present — an included seat sends none (removed the
  blank-seatPriceId guard/throw).
- **ViewModel**: `canAddMember` no longer requires a seat price; the add sends
  none (included/free). Removed the now-unused `seatPriceId` (cheapest-line)
  heuristic.
- **UI**: the "no seat price configured" dead-end message is gone, and every open
  spot shows the gold **Invite** action (33B), regardless of seat price.

The other card states were already correct: `familyRow` renders **Active /
Invite-sent (+ Resend) / Remove**; `resendInvite` and `removeFamilyMember` already
exist.

## Scope / not done (follow-up)

**Additional (chargeable, beyond-included) seats** are not surfaced. The app's
`Entitlement` has no `maxAdditionalSeats` / `additionalSubaccountFeeCents`, and the
member-client seat-price resolution (`findSeatProduct` over the catalogue) is a
bigger piece tied to Innocent's Finance/seat-pricing work. So today the app offers
exactly the plan's **included** spots. The header counts `includedSubaccounts`
accordingly. Adding paid additional seats is a separate task.

## Backend dependency

This relies on the gateway accepting an `addSubaccount` for an **included** seat
with **no** `seatPriceID` — which member-client already does, so it should be
safe. Worth a one-line confirm from Innocent given dev has no seat line configured.

## Files

- Swift: `Core/Network/AsiApi.swift`, `Feature/Account/AccountViewModel.swift`,
  `Feature/Account/AccountScreen.swift`; test `AccountViewModelTests.swift`.
- Kotlin: `core/network/AsiApi.kt`, `feature/account/AccountViewModel.kt`,
  `feature/account/AccountScreen.kt`; test `AccountViewModelTest.kt`.

## Tests

Replaced the two obsolete seat-price tests with
`anIncludedSeatIsAddableWithoutASeatPrice` / `an included seat is addable without a
seat price` (a base-line-only plan can still add), and updated the add test to
assert **no** `seatPriceID` is sent.

- Swift: `AccountViewModelTests` (single-process, iPhone 16 Pro) → **38 tests
  passed**, `** TEST SUCCEEDED **`.
- Kotlin: `AccountViewModelTest` → **BUILD SUCCESSFUL**.
