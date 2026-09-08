# Scope — native guest login door (mobile), mirroring member-client #155/#157

**Date:** 2026-09-08 · **Status:** ✅ BUILT & shipped on both platforms (dev).
See `journals/2026-09-08-guest-login-door.md` for the as-built record.
**Decisions locked:** entry lives on the **Login screen** (mirror member-client);
**include** the `passwordSignInAvailable` gating (with retry-safety).

## Bottom line

**Client-only feature — no backend changes.** The gateway already serves every
piece member-client uses against it: OTP login already stamps `origin=APP` (so a
new email is born a **Guest User**), `verifyLoginOtp` accepts `firstName`/`lastName`
and stamps the display name only when the account has none, `requestLoginOtp` can
return `passwordSignInAvailable`, and `updateMyContactInfo` is self-scoped. Both
mobile apps already have the OTP flow, guest **detection** (`accountStatus.code ==
guest_user/member_lead`, `isGuest`, `GuestUpsellSheet`), and a reusable first/last
name UI (ProfileCompletion contact pane). The net-new work is a login **entry +
name pane**, two small API deltas, the password gating, and a name safety-net.

## Target flow (post-#157)

```
Login (email) ──"Continue as a guest"──▶ Guest pane
                                          first name · last name · email
                                          [ Create Account ]
                                              │  (mark usedGuestDoor)
                                              ▼
                                          Code (OTP, 4 digits)
                                          "Use password instead"  ← only if passwordSignInAvailable
                                              │
                                              ▼
                                   verifyLoginOtp(origin=APP, firstName, lastName)
                                     → server stamps display name iff account had none
                                              ▼
                            [safety net] GuestNameScreen — only if usedGuestDoor && displayName blank
```

Returning guest: email + code only — the name is already on the account, never re-asked.

## Work items (both platforms, mirrored)

### 1. API (AsiApi + Models)
- `requestLoginOtp` — request `passwordSignInAvailable` in the selection set; add it to
  `OtpRequest` (default **false**). Add an **unknown-field retry**: if the gql error is a
  "cannot query field passwordSignInAvailable" error, re-issue the mutation *without* the
  field and default the flag false (gateway introspection can lag a minute after deploy).
- `verifyLoginOtp` — add optional `firstName`/`lastName` variables (`$firstName: String,
  $lastName: String`) to the existing mutation; pass through, trimmed→nil. `origin=APP`
  stays the default. (No signature change for existing callers — params are optional.)

### 2. Login state + screen
- LoginViewModel: add a **guest mode** (Swift `LoginStep.guest` / Kotlin `LoginStep.Guest`)
  plus `guestFirstName` / `guestLastName`; `continueAsGuest()` enters it and sets the
  in-memory guest-door flag. Guest submit validates names+email → `requestLoginOtp` → Code
  step, remembering guest mode + names. On verify in guest mode, call
  `verifyLoginOtp(..., firstName, lastName)`.
- LoginScreen: add the **"Continue as a guest"** button on the email pane and the **guest
  pane** (two name fields + email, "Create Account", "Already registered? Log in" back link).
- **Password gating:** move/gate the "Use password instead" affordance to the **Code**
  step, shown only when `passwordSignInAvailable == true` (matches member-client — the flag
  is only known after `requestLoginOtp`). NB: this slightly changes the existing-member
  password entry (request a code first, then the link appears) — the same tradeoff
  member-client accepted ("one extra tap for a member with a password, nothing for anyone
  else").

### 3. Guest-door marker + name safety-net
- **Marker:** an **in-memory** session flag (`usedGuestDoor`), NOT persisted — mobile's "one
  journey" is one app launch. Set on entering the guest pane; cleared once a display name
  is present. (member-client uses sessionStorage for the same reason.)
- **Safety net:** a small post-login name screen shown only when `usedGuestDoor &&
  member.displayName isBlank`; collects first/last → `updateMyContactInfo(displayName:)` →
  patch session displayName. Reuses the ProfileCompletion two-field UI. New shell
  destination (`.guestName`) gated like the other post-login gates. In practice rarely hit,
  since the name is captured pre-OTP and stamped at creation — it's a true fallback.

### 4. Copy (verbatim from member-client `lib/guestDoor.ts`)
`"Continue as a guest"`, heading `"Explore as a guest"`, body `"Explore the Attorney Shield
app as a guest before you join. We will email you a code to verify that it's you. You must
purchase a membership to connect with an attorney."`, action `"Create Account"`, back link
`"Already Registered? Login"`, name heading `"What should we call you?"`, name body `"Your
name is all we need to set up your guest access. Next time, your email and a code are enough."`

### 5. Tests (per platform)
- AsiApi: `requestLoginOtp` parses `passwordSignInAvailable`; the unknown-field retry path;
  `verifyLoginOtp` sends `firstName`/`lastName`.
- LoginViewModel: `continueAsGuest` enters guest mode; guest submit requests an OTP; verify
  in guest mode passes the names; password affordance gated by the flag.
- Safety-net: shown iff guest-door + blank name.

## Files (per platform)
`Core/Network/AsiApi` + `Models` · `Feature/Auth|Login/LoginViewModel` + `LoginScreen` ·
`Core/Session/SessionManager` (marker + post-verify name) · shell (`AttorneyShieldApp` /
`MainActivity` — `.guestName` destination + gate) · new `GuestNameScreen`/pane · copy
constants · the three test files above.

## Effort & phasing
**Medium — ~1 focused day per platform** (~2 sessions with the mirror-both discipline).
Phase 1 API deltas + tests → Phase 2 guest pane/state/entry + password gating → Phase 3
marker + safety-net → Phase 4 copy/polish, full suites, journal, commit/push (kotlin→dev,
swift→dev, asi-claude→main).

## Risks / notes
- `passwordSignInAvailable` gateway lag → covered by the unknown-field retry.
- Password entry moves behind a code request (member-client-accepted tradeoff).
- No backend asks; but worth a one-line heads-up to Innocent that mobile is adopting the
  same `verifyLoginOtp` name-stamp + `passwordSignInAvailable` contract member-client uses.
