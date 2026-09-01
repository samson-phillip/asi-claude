# 2026-09-01 — Home after login: "Protected, there" + empty tiles

## Symptom

On iOS, immediately after signing in the Home screen showed the greeting
**"Protected, there"** (the `there` fallback) and the four "What's happening?"
tiles were empty skeletons that never resolved.

## Root cause

Both were fallout from the account-switch fix (recreating the `@State` view
models when `session.member.userId` changes):

1. **Empty tiles** — recreating the `home` VM does *not* re-fire an un-keyed
   SwiftUI `.task { await home.load() }`. The screen kept the *old* task bound to
   the *discarded* VM, so the fresh VM never loaded → permanent skeletons.
2. **"there" greeting** — `greetingName`/`initial` were assigned once in the
   VM's `init` from `session.member`. The display name resolves a beat *after*
   sign-in (via `refreshContext`), so the snapshot captured the empty state and
   never caught up.

## Fix

**iOS** (`swift`):
- `HomeViewModel.swift` — `greetingName`/`initial` are now **computed** live from
  `session.member` (reading `session.member` inside the computed body makes the
  view re-render when the member changes). Removed the init-time assignment.
- `AttorneyShieldApp.swift` — keyed all four screen loads on the member so a VM
  swap (or the name resolving) re-fires the load:
  `.task(id: session.member?.userId) { await <vm>.load() }` for home, activity,
  account, and glovebox.

**Android** (`kotlin`) — parity for the same latent greeting bug:
- `HomeViewModel.kt` `init` — seed the greeting immediately from
  `session.member.value` (keeps the synchronous value the tests assert), then
  **collect `session.member`** for the lifetime of the VM so the greeting tracks
  the name resolving and account switches. Extracted `applyGreeting(member)` to
  share the mapping.
- Android's empty-tiles path was already sound: account switch clears the
  `ViewModelStore`, and `LaunchedEffect` on the fresh VM re-runs `load()`. No
  tile change needed.

## Tests

- iOS `HomeViewModelTests` — **15/15 pass**; app build **SUCCEEDED**.
- Android `HomeViewModelTest` — **green** (incl. "greeting comes from the
  session" and "T-H-10 falls back to the email local part", which assert the
  synchronous seed value).

## Files

- Swift: `AttorneyShield/Feature/Home/HomeViewModel.swift`,
  `AttorneyShield/AttorneyShieldApp.swift`.
- Kotlin: `app/src/main/java/com/attorneyshield/member/feature/home/HomeViewModel.kt`.

## Next

- On-device re-check after login (fresh account **and** account switch) that the
  greeting shows the real first name and the tiles populate on both platforms.
