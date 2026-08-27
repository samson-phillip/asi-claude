# 2026-08-27 — Fire the trial gate (V2) for trial accounts

## Task

A trial account (`x1@…`) signed in, tapped to connect, and got the plain
Connecting screen with no LFR rung — instead of the CodePen V2 trial gate. Product
decision (confirmed): **gate trials per the CodePen** (they conflict with
member-client, which lets trials connect). Fix the detection so the gate fires.
Repos: `kotlin`, `swift`. Full analysis in
`notes/account-states-trial-grace-guest-profile.md`.

## Root cause

`HomeUiState.isTrial` gated only on `membership.isTrial`, which was
`myMembership.status.code == "trialing"`. But:

- the backend's trial status value is **`"trial"`** (`member-client` `guest.tsx`
  gates on `["active","trial"]`), not `"trialing"`;
- the authoritative segmentation is **`myAccountStatus.code == "trial_member"`**
  — which the app *already fetches* into `MemberContext.accountStatus` at sign-in
  but consumed nowhere.

So `isTrial` was always false → the V2 gate (already built) never opened → the
trial fell through to a normal `member-call` the backend won't route for a trial
→ Connecting with no LFR (now → "No attorney picked up" after the ring-timeout
fix).

## Change

- `Membership.isTrial` → `statusCode in {"trial","trialing"}` (both platforms).
- `HomeUiState.isTrial` (Kotlin) / `HomeViewModel.isTrial` (Swift) → ORs the
  membership status with `accountStatusCode == "trial_member"`, so a
  freshly-created trial whose membership row hasn't landed is still gated.
- `HomeViewModel.load()` surfaces `session.member.accountStatus.code` into state.

## Verification

| Suite | Result |
|---|---|
| Android — `testDebugUnitTest` | **BUILD SUCCESSFUL** (added: trial opens on either word; segmentation opens it without a membership; a member is never gated) |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

**End-to-end not verified here:** my emulator is signed in as a full member
(John), not a trial, so I can't reproduce the trial gate locally. Needs a check on
the trial device/account: sign in as the trial → tap the shield/a tile → the V2
gate ("You're on a trial…") should appear instead of Connecting.

## Not done (deliberately, needs product + backend — see the profile doc)

- **Guest** upsell gate (G3) on the connect path — not built at all.
- **Grace / expired** handling on the connect path (Account shows grace only).
- Gating the call on `membershipEntitlement.entitled` as the single truth.
- Backend questions filed in the profile: the reliable trial signal for a fresh
  app trial (segmentation can be null until reconciled), and whether routing
  **rejects** an unentitled member's call so a bypass fails safe.

## Files

- **kotlin** — `core/network/AccountModels.kt`, `feature/home/HomeViewModel.kt`,
  `feature/home/HomeViewModelTest.kt`, `feature/trial/TrialViewModelTest.kt`.
- **swift** — `Core/Network/AccountModels.swift`, `Feature/Home/HomeViewModel.swift`.
