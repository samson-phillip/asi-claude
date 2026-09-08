# 2026-09-08 — Native guest login door (both platforms)

Built the native **guest login door** (member-client "Guest User Capture Flow",
#155/#157) on Android + iOS. Scoped first in
`asi-claude/notes/guest-login-door-scope.md`; Samson locked two decisions —
**entry on the Login screen** (mirror member-client) and **include the
`passwordSignInAvailable` gating** with retry-safety — then approved the build.

## Why it was small: no backend changes

The gateway already serves every piece member-client drives against it. OTP login
**already stamps `origin=APP`**, so an email that verifies a code is born a **Guest
User** — the mechanism existed. What was missing was purely client-side: a name
pane, two small API deltas, the password gating, and a name safety net.

## The flow (post-#157)

Login (email) → **"Continue as a guest"** → guest pane (first name · last name ·
email, "Create Account") → OTP code → `verifyLoginOtp(origin=APP, firstName,
lastName)`. The server stamps the display name **only** on a brand-new account, so
a returning guest (email + code only) is never renamed. "Use password instead"
shows on the code pane **only when `passwordSignInAvailable`**. A `GuestNameScreen`
is a fallback, shown only if a guest-door session lands with no display name.

## What changed (both platforms, mirrored)

- **API** (`AsiApi` + models): `requestLoginOtp` now requests
  `passwordSignInAvailable` and **retries without the field** if the gateway
  rejects it (a federated field can lag introspection; without the retry the whole
  login screen breaks). `verifyLoginOtp` gained optional `firstName`/`lastName`
  (null for ordinary sign-in; `origin=APP` unchanged).
- **SessionManager**: in-memory `usedGuestDoor` marker (NOT persisted — one app
  launch, like member-client's sessionStorage), cleared on sign-out and once a
  name is set; `signInWithOtp` threads the names; new `saveGuestName` (self-scoped
  `updateMyContactInfo`, patches the member + spends the marker).
- **LoginViewModel**: `guest` step + `guestFirstName`/`guestLastName`/`isGuestFlow`
  /`passwordSignInAvailable`; `continueAsGuest` (marks the session) / `backToLogin`
  (drops it); `verify` passes names only in the guest flow; back-from-code returns
  to the guest pane.
- **LoginScreen**: "Continue as a guest" on the email pane; a guest pane; the code
  pane's "Use password instead" gated on the flag.
- **Shell** (`MainActivity` / `AttorneyShieldApp`): a `guestName` destination; the
  post-sign-in route sends a nameless guest there, else drops the marker and goes
  to the checklist; leaving sign-in clears the marker.
- **New**: `GuestNameScreen` (both), copy verbatim from member-client
  (`Explore as a guest` / `Create Account` / `What should we call you?` …).

## Tests

- **Android** (`:app:testDebugUnitTest` green): `LoginViewModelTest` +7 (guest mode,
  names into verify, password gating, back-out), `AsiApiTest` +5 (passwordSignInAvailable
  parse + unknown-field retry + genuine-error-not-swallowed + verify names/null),
  `SessionManagerTest` +1 (`saveGuestName`).
- **iOS** (`AttorneyShieldTests` green, `** TEST SUCCEEDED **`): the same set mirrored
  across `LoginViewModelTests` / `AsiApiTests` / `SessionManagerTests`.

## Files

- Kotlin: `core/network/AsiApi.kt`, `core/network/Models.kt`,
  `core/session/SessionManager.kt`, `feature/auth/LoginViewModel.kt`,
  `feature/auth/LoginScreen.kt`, `feature/auth/GuestNameScreen.kt` (new),
  `MainActivity.kt`; tests `LoginViewModelTest`, `AsiApiTest`, `SessionManagerTest`.
- Swift: `Core/Network/AsiApi.swift`, `Core/Network/Models.swift`,
  `Core/Session/SessionManager.swift`, `Feature/Auth/LoginViewModel.swift`,
  `Feature/Auth/LoginScreen.swift`, `Feature/Auth/GuestNameScreen.swift` (new),
  `AttorneyShieldApp.swift`; tests `LoginViewModelTests`, `AsiApiTests`,
  `SessionManagerTests`.

## Notes

- The password entry now lives behind a code request (member-client's accepted
  tradeoff): the email screen still offers "Use your password instead", but the
  gated "Use password instead" on the code screen only appears when the server
  confirms a password exists.
- Worth a one-line heads-up to Innocent: mobile now adopts the same
  `verifyLoginOtp` name-stamp + `passwordSignInAvailable` contract member-client
  uses — no backend ask, just confirming the shared contract.
