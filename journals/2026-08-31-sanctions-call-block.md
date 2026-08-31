# 2026-08-31 — Sanctions call-block (403 on member-call)

## Task

Innocent's platform feedback (II.1.f) adds a Sanctions **"Disable"** flag that
must **block the member from requesting legal support**. This is the mobile
half of that safety control.

## How the reference actually does it (settles the design)

I scoped this expecting a pre-call `myAccountRestriction { code, reason }` query.
It does not exist. member-client enforces sanctions at **call-initiation**, on
the comms REST endpoint, not via a GraphQL gate:

- `startMemberCall` → `POST /api/vonage/video/member-call`. On **HTTP 403** it
  throws `SanctionedError`, reading the **403 body** as the reason (fallback:
  *"This account is currently blocked from requesting legal support."*).
  `CallScreen` shows it on the error phase; it is **not** a logout.
  (`member-client/src/lib/api.ts` `SanctionedError` + the 403 branch of
  `startMemberCall`; `CallScreen.tsx` catch → `phase = "error"`.)

So there is **nothing to invent** — I mirror the 403 handling. This also matches
CLAUDE.md's "do not invent new endpoints."

## The bug this fixes

Both apps mapped member-call **403 → `UnauthorizedError`/`UnauthorizedException`**
(the same branch as 401), which forces a **sign-out**. So the moment the backend
starts returning 403 for a disabled account, a sanctioned member would be *logged
out* instead of shown why they're blocked. Now:

- **401** → session expired → sign back in (unchanged).
- **403** → `SanctionedError`/`SanctionedException(bodyReason)` → terminal error
  phase, shows the server's reason, **no logout**, **not retryable** (`canRetry`
  stays false for the error phase — renewing only 403s again until the block is
  lifted).
- **409** → no attorney (unchanged, retryable).

Only the member-call REST path changed. The GraphQL path still treats 403 as auth
(a 403 there really is a rejected token).

## Files

- Swift: `Core/Network/AsiApi.swift` (new `SanctionedError`; 401/403 split in
  `startMemberCall`), `Feature/Call/CallViewModel.swift` (catch `SanctionedError`
  → `fail`); test `AttorneyShieldTests/CallViewModelTests.swift`.
- Kotlin: `core/network/AsiApi.kt` (new `SanctionedException`; 401/403 split),
  `feature/call/CallViewModel.kt` (catch `SanctionedException` → `fail`); test
  `feature/call/CallViewModelTest.kt`.

## Tests

New on both platforms: a 403 with a body shows that reason on the error phase and
is **not** retryable; a 403 with an empty body falls back to the standard block
message.

- Swift: `CallViewModelTests` (single-process, iPhone 16 Pro) → **24 tests
  passed**, `** TEST SUCCEEDED **`.
- Kotlin: `CallViewModelTest` → **BUILD SUCCESSFUL**.

## For Innocent (confirm the contract)

The apps now honour a **403 from `POST /api/vonage/video/member-call`** as the
sanctions block, using the **response body as the member-facing reason** (empty →
our standard message). Please confirm the gateway returns 403 (not 401/423) for a
Disabled account, and whether the body is plain text or JSON — member-client
treats it as plain text and so do we.
