# 2026-08-31 — Family members: gate the whole screen on `isSubaccount`

## Task

Follow-up to the included-seats fix. A member who is themselves a **family
child** (a sub-account on someone else's plan) must not be able to add or manage
members — otherwise a child could invite strangers onto the **primary holder's**
plan. Innocent's Round Two confirmed the `Entitlement` already exposes
`isSubaccount`, and that it must gate the entire Family screen. Also fetch the two
seat fields the earlier task noted as missing.

## Changes (both platforms)

- **`Entitlement` / `GqlEntitlement`**: added `maxAdditionalSeats` and
  `additionalSubaccountFeeCents` (the paid-seat fields; `isSubaccount` and
  `includedSubaccounts` already existed). The `getEntitlement` query now asks for
  both new fields and maps them.
- **`canAddMember`**: now `!isSubaccount && addMember.isComplete &&
  !isAddingMember && openSeats > 0`. A sub-account can never satisfy it.
- **Family pane**: when `isSubaccount`, the pane short-circuits to a
  **"Managed by the primary account"** card — *"You're on a family membership.
  Only the primary account holder can add or manage members."* — instead of the
  seat list / Invite UI.
- **Account overview**: the **Family members** nav row is hidden for
  sub-accounts (and the preceding Emergency-contacts row drops its divider so the
  group closes cleanly), matching the fact that they have nothing to manage there.

## Why gate rather than error

The backend refuses an `addSubaccount` from a child, but a hidden dead-end button
that only fails on tap is a bad experience and leaks the primary's seat model into
the child's UI. Gating on the entitlement flag we already load keeps the child's
Account screen honest and quiet.

## Not done (still blocked — needs Innocent)

**Paid additional seats.** We now *fetch* `maxAdditionalSeats` /
`additionalSubaccountFeeCents`, but adding a beyond-included seat needs a
`seatPriceId` whose source (catalogue `findSeatProduct` in member-client) is tied
to Innocent's Finance/seat-pricing work. Today the app still offers only the
plan's **included** spots. Where the seat price id should come from on mobile is
the open question to send him.

## Files

- Swift: `Core/Network/AccountModels.swift`, `Core/Network/AsiApi.swift`,
  `Feature/Account/AccountViewModel.swift`, `Feature/Account/AccountScreen.swift`;
  test `AccountViewModelTests.swift`.
- Kotlin: `core/network/AccountModels.kt`, `core/network/AsiApi.kt`,
  `feature/account/AccountViewModel.kt`, `feature/account/AccountScreen.kt`; test
  `AccountViewModelTest.kt`.

## Tests

New: `aSubAccountCannotAddMembers` / `a sub-account cannot add members` — an
entitlement with `isSubaccount:true` yields `isSubaccount == true` and
`canAddMember == false`, even with a complete add-member form.

- Swift: `AccountViewModelTests` (single-process, iPhone 16 Pro) → **39 tests
  passed**, `** TEST SUCCEEDED **`.
- Kotlin: `AccountViewModelTest` → **BUILD SUCCESSFUL**, 18 tests.
