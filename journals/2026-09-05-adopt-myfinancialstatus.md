# 2026-09-05 — Adopt myFinancialStatus (backend round-two)

## Context

Checked Innocent's shared artifacts for updates. The **"Answers for round two"**
artifact (`9c6eb93c`, backend, 31 Aug) had real replies. Two safe wins picked:

1. **Document device-region** — turned out to be **already done**: both platforms
   already pass `TimeZoneCountry.current()` (device region) to `listDocumentFields`,
   matching the backend ask and member-client. The "some types don't appear" is the
   backend's own data issue (no global document types on dev — Innocent is raising
   which are universal with David). No mobile change.
2. **`myFinancialStatus`** — now shipped (dev + uat). Adopted it.

## myFinancialStatus

Contract (from the artifact): `myFinancialStatus: MemberStatusRef { code name }` —
same shape/self-scoping as `myAccountStatus`; codes `current` / `grace_period` /
`expired` / `canceled`; **null = not reconciled yet → fall back to entitlement**.
Our `PlanStatus` was already documented as this taxonomy; the membership/entitlement
derivation was the stopgap until the field shipped. member-client has **not** adopted
it yet (only pre-login `purchaseEligibility.financialStatus`), so we implement per
the backend contract with the derivation as the null-fallback.

Both platforms:
- `AsiApi.myFinancialStatus()` / `getMyFinancialStatus()` (mirrors the account-status
  query) + `MyFinancialStatusData` model.
- `AccountViewModel` fetches it best-effort in `load()` and stores it.
- `PlanStatus.of(…, financialStatus)` — when present, key on the stable `code`,
  show the server `name`; unknown code or null → the existing inference (a defaulted
  param, so existing callers/tests are unchanged).
- Call site (Account plan card) passes it.

Tests: added `planStatusPrefersMyFinancialStatusWhenPresent` (both platforms) —
covers each code, unknown-code fall-through, and null fallback. The account-load
tests gained a `myFinancialStatus: null` stub so they stay on the fallback path.

## Status

- **Android: `testDebugUnitTest` green**, including the new test. Committed.
- **iOS: code complete (faithful mirror), but could NOT compile/test locally** — the
  machine is at **95% disk (≈0.7 GB free)** and SPM cannot clone stripe-ios/lottie-ios
  (evicted from cache). Not a code issue. iOS commit is held until it compiles once
  disk is freed (clearing Xcode DerivedData ~895M / Archives 1.6G would do it).

## Still to decide (deferred to user)

- **Deep-link domain** conflict from the same artifact: backend offers
  `attorneyshield.io` (they host `/.well-known/` per env) and says
  `attorney-shield.com` is Webflow with nothing serving it, and the return path
  should be `/app/return?email=` — which contradicts our recorded E1 "stay on
  attorney-shield.com, never .io." Awaiting the user's ruling.
- Other round-two items: `myAccountRestriction { code }` typed sanctions query
  (we use the member-call 403 today), and specifying where the additional-seat
  `seatPriceId` should live.

## Files

- Kotlin: `core/network/AsiApi.kt`, `core/network/Models.kt`,
  `feature/account/AccountViewModel.kt`, `feature/account/AccountScreen.kt`,
  + `AccountViewModelTest.kt`.
- Swift (pending compile): `Core/Network/AsiApi.swift`, `Core/Network/Models.swift`,
  `Feature/Account/AccountViewModel.swift`, `Feature/Account/AccountScreen.swift`,
  + `AccountViewModelTests.swift`.
