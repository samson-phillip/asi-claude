# 2026-08-28 — Change Password: live requirement checklist (a leaf from Set-a-password)

## Task

Improve the Change Password screen by taking a cue from the CodePen "Set a
password" screen the user shared. The distinguishing feature there is the **live
requirement checklist with green ticks** ("At least 8 characters / 1 number /
1 symbol") that flip green as the new password satisfies each rule. Change
Password only had a plain "At least 8 characters" hint.

## The leaf picked

The live 3-rule requirement checklist (`AsiRequirementRow`), reusing the **same
rules** our own Set-a-password step already enforces — so a new password is held
to one standard wherever it is set. Not brought over: the steel-blue "a password
makes sign-in faster…" info chip — that copy is specific to *creating* an
optional password during onboarding and would be inaccurate on Change Password.

Behaviour note: `member-client`'s Change Password only enforces length (8), while
its Set Password enforces all three. We intentionally hold Change Password to all
three — stricter is safer and it keeps our two password screens consistent (a
client-side gate; no backend contract changes).

## One source of truth for the rules

Reused the existing rule helper rather than duplicating the logic:
- Kotlin: `ChangePasswordForm.rules = CompletionUiState.rulesFor(next)`.
- Swift: `ChangePasswordForm.rules = ProfileCompletionViewModel.rulesFor(next)`.

`isComplete` now requires `rules.allMet && matches && current not-blank` (was
`isLongEnough && …`). The New-password field's "At least 8 characters"
supportingText is replaced by the three live `AsiRequirementRow`s below the
Confirm field; the "These do not match" confirm hint stays.

### Swift concurrency fix

`ProfileCompletionViewModel` is `@MainActor`, so its `static func rulesFor` was
MainActor-isolated and couldn't be called from the nonisolated
`ChangePasswordForm` struct (hard error even in Swift 5 mode). Marked the pure
helper (and `minPasswordLength`) **`nonisolated`** — correct, since it touches no
actor state — so it's callable from anywhere.

## Repos & files touched

- `kotlin`
  - `feature/account/AccountViewModel.kt` — `ChangePasswordForm.rules` +
    `isComplete` via profile `rulesFor`; imports.
  - `feature/account/AccountScreen.kt` — `ChangePasswordPane` shows the 3
    `AsiRequirementRow`s; dropped the length hint; import.
  - `AccountViewModelTest.kt` — updated the 3 password-change tests to strong
    passwords + a new "long but no number/symbol is rejected" assertion.
- `swift`
  - `Feature/Account/AccountViewModel.swift` — same `rules`/`isComplete`.
  - `Feature/Account/AccountScreen.swift` — checklist in `changePasswordPane`.
  - `Feature/Profile/ProfileCompletionViewModel.swift` — `nonisolated` on
    `rulesFor` + `minPasswordLength`.
  - `AccountViewModelTests.swift` — same test updates.

## Test results

- **Android**: `AccountViewModelTest` (incl. updated password tests) — **all
  pass**; main compiles.
- **iOS**: `xcodebuild build` — **BUILD SUCCEEDED**; `AccountViewModelTests` +
  `ProfileCompletionViewModelTests` — **TEST SUCCEEDED**.

## Open issue — live screenshot still pending

Same as the Settings entry: the emulator session is expired and I did not scan
for credentials, so no live capture of the Change Password checklist this
session. It reuses `AsiRequirementRow`, already verified live on the
Set-a-password screen. Easy to capture once signed in.
