# 2026-08-30 — Honor opt-outs: tour guard hardening + notifications→nudge gate

## Task

The member reported that opt-outs weren't being honored — the guided tour
reappeared on relaunch after choosing not to show it again, and turning
notifications off didn't stop the in-app prompts.

## Investigation (what I found before changing anything)

Traced the full persistence path on both platforms. The core plumbing was
already correct and well-tested:
- "Don't remind me" → per-step permanent silence; "Maybe later" → 3-day snooze;
  tour skip/finish → `setSeenTour(true)`. All scoped **per member**, persisted
  (SharedPreferences / UserDefaults), and honored by `NudgePolicy` / the tour
  gate. Session (incl. `userId`) restores synchronously before Home, so the
  launch read and the dismissal write land in the same bucket. Store-level tests
  already cover "dismiss → new store instance (relaunch) → still seen".

So the reported tour re-show was a **narrow residual**, and I found one genuine
**disconnect** in notifications:

## Fix 1 — Tour guard: mark seen the moment it opens

`tour_seen` was written only on explicit Skip/Finish. If the app was killed while
the tour was still on screen (mid-step or on the completion card, before tapping
anything), it was never marked seen and reappeared next launch. Now the launch
gate marks it seen the instant it opens, so **no exit path** — background,
force-quit, crash — can bring it back. Replay-from-Settings runs the tour
directly, past the gate, so it still works.

- kotlin: `MainActivity.kt` — `setSeenTour(true)` in the first-launch
  `LaunchedEffect` before setting the tour running.
- swift: `AttorneyShieldApp.swift` — same in the Home `.task`.

## Fix 2 — Notification settings now actually gate the in-app nudge

The real bug behind "turning notifications off doesn't stop nudges": the
Notification Settings screen wrote only to the **server** profile
(`updateNotificationPreferences`), while the Home nudge (screen 25) is gated by a
**separate local** flag (`NudgeState.notificationsEnabled`) that nothing ever
set. So the master switch / frequency dial / Setup-reminders category had no
effect on the in-app nudge.

Bridged them: `NotificationsViewModel` now mirrors the effective preference into
the local nudge store whenever preferences load or change. The Home nudge is a
"Finish setup" prompt, so it's allowed only when **master on AND frequency ≠ Off
AND Setup-reminders on** (`categoriesApply && notifySetupReminders`). Applied
optimistically on toggle and re-synced from the server response; reverted with
the preferences if the save fails.

- kotlin: `feature/notifications/NotificationsViewModel.kt` — `nudgeStore` param
  + `syncNudgeGate(prefs)` in `load` / `setPreferences`; wired `nudgeStore =
  tourStore` at both call sites in `MainActivity.kt`.
- swift: `Feature/Notifications/NotificationsViewModel.swift` — same; wired
  `nudgeStore: shared` in `AttorneyShieldApp.swift`.

## Decisions

- **Mark-seen-on-launch** (vs only on dismissal): the user's goal is "it should
  not keep coming up." Marking on open makes the guard bulletproof against every
  exit path; the tour is a one-time gentle intro and remains replayable from
  Settings, so nothing is lost.
- **Which controls gate the nudge**: the in-app nudge is specifically a setup
  reminder, so it honors the master switch, the frequency Off, and the
  Setup-reminders category — not the Tips/Billing categories (those drive other
  notifications, not this prompt).
- **Reused the existing single local flag** rather than adding per-category local
  state — minimal, and the derived boolean fully captures "should the Home nudge
  fire".

## Test results

- **Android**: full `:app:testDebugUnitTest` — BUILD SUCCESSFUL. New tests:
  turning notifications off (and frequency Off) flips the local nudge gate.
  Existing tour/nudge store tests still green.
- **iOS**: `xcodebuild build test` (Notifications + NudgeStore + TourStep) — BUILD
  + TEST SUCCEEDED. Mirrored the two nudge-gate tests.

## Notes / not done

- Per-step "Don't remind me" and "Maybe later" were already correct — left as-is.
- Safety-critical nudges are still suppressed by the master-off gate (the local
  state carries no per-category exemption). If we later want safety-critical to
  survive a master-off, that's a `NudgePolicy` change + richer local state — out
  of scope here.
- Live screenshot still pending (emulator session expired).
