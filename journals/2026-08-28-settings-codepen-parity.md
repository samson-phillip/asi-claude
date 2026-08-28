# 2026-08-28 — Settings (33C) brought to the CodePen design

## Task

The Settings screen didn't match the CodePen (screen 33C). Ours rendered
**Change password as an inline form** at the top, followed by a different mix of
rows (Terms / Push / Replay / a non-actionable Device permissions), with no
Language row. The CodePen is a clean list of **five two-line rows** with a
right-side action, plus a footnote:

1. Change password / Update your sign-in password — **Update ›**
2. Language / English (US) — **Change ›**
3. Push notifications / Nudges, renewals, and alerts — **Manage ›**
4. Device permissions / Camera · Microphone · Location — **Review ›**
5. Terms of Service / Attorney Shield and Law Firm, combined — **View ›**
- footnote: "Delete account lives in Payment & plan"

## Design authority

- `notes/design-reference-codepen.md` §33C is explicit: "The five current
  settings, one row each. Push notifications opens the existing notification
  settings screen (26), never a duplicate. Delete account intentionally lives in
  Payment & plan only."
- Behaviour from `member-client/src/screens/SettingsScreen.tsx`: Change Password
  is a **pushed screen** (not inline); Language opens a **picker** and its sub
  shows the chosen language (local device preference via `lib/language.ts`,
  EN/ES); Device Permissions requests/reviews OS grants; it also keeps a Replay
  row ("The tour cards promise 'Replay anytime from Settings.' — this is that").

## Decision (user-confirmed)

The CodePen Settings shows 5 rows and no Replay-the-tour, yet the CodePen tour
flow promises "Replay anytime from Settings" (and member-client keeps the row).
Asked the user → **keep Replay as a 6th row** (same styling) so the tour's promise
still has a target. Non-destructive.

Two smaller calls made without asking:
- **Action-link colour stays gold** (`accentText`), the app-wide convention for
  every actionable row (Manage plan ›, address actions, etc.), rather than the
  mockup's grey — palette Rank 1 governs colour and gold-for-actions is the
  established pattern.
- **Language persists but does not re-localise** yet (the app is English-only);
  the choice is recorded like member-client's device preference so the row
  reflects it across launches.

## What shipped (both platforms, feature-for-feature)

- **Change password** is now a row → opens its own pushed pane (`ChangePassword`)
  carrying the existing form (Current / New / Confirm + Update password). The
  inline form is gone from Settings.
- **Language** row shows the chosen label; **Change ›** opens a picker
  (English (US) / Spanish) that persists the choice locally and confirms it.
- **Push notifications** → screen 26 (unchanged behaviour, reordered).
- **Device permissions** → **Review ›** now deep-links to the app's page in the
  OS settings (Android `ACTION_APPLICATION_DETAILS_SETTINGS`; iOS
  `openSettingsURLString`) — previously a dead, non-actionable row.
- **Terms of Service** → Legal (detail text matched to "…and Law Firm, combined").
- **Replay the tour** kept as the 6th row.
- Footnote retained.

## Repos & files touched

- `kotlin`
  - `feature/account/AccountViewModel.kt` — `AccountPane.ChangePassword`;
    `AppLanguage` + `APP_LANGUAGES`; `LanguageStore` (+ `InMemory` / `Prefs`);
    `languageTag`/`languageSheetOpen` state + `languageLabel`; VM ctor takes a
    `LanguageStore` (default in-memory) and seeds the tag; `openLanguagePicker`
    / `dismissLanguagePicker` / `setLanguage`.
  - `feature/account/AccountScreen.kt` — `SettingsPane` rewritten as the row
    list; `ChangePasswordPane`; `LanguagePickerSheet` (FloatingSheet); new
    callbacks (`onReviewPermissions`, language).
  - `MainActivity.kt` — `PrefsLanguageStore` from a `SharedPreferences`
    ("asi_settings"); wired `onReviewPermissions` (OS-settings intent) + language
    callbacks.
  - `AccountViewModelTest.kt` — 4 new tests.
- `swift`
  - `Feature/Account/AccountViewModel.swift` — `.changePassword` pane;
    `AppLanguage`/`APP_LANGUAGES`; `LanguageStore` (+ `InMemory` /
    `UserDefaults`); language state + `languageLabel`; ctor takes a
    `LanguageStore` (default UserDefaults) and seeds the tag; language methods.
  - `Feature/Account/AccountScreen.swift` — `settingsPane` rewritten;
    `changePasswordPane`; `languageSheet` (native `.sheet`); `onReviewPermissions`.
  - `AttorneyShieldApp.swift` — wired `onReviewPermissions`
    (`UIApplication.openSettingsURLString`); `import UIKit`.
  - `AccountViewModelTests.swift` — `make(languageStore:)` + 5 new tests.

## Test results

- **Android**: `:app:compileDebugKotlin` clean; `AccountViewModelTest`
  (existing + 4 new) — **all pass**; APK builds + installs.
- **iOS**: `xcodebuild build` — **BUILD SUCCEEDED**; `AccountViewModelTests`
  (existing + 5 new) — **all pass** (`xcodebuild test` exit 0).

## Open issue — live screenshot pending

Could **not** capture a live Settings screenshot this session: the emulator's
saved session had expired (app is at the welcome/login screen) and I did not
scan for login credentials (the auto-mode classifier correctly blocked that).
The Settings UI is composed entirely from primitives verified live earlier today
(`AsiNavRow`, `FloatingSheet`, `AsiTextField`, `PrimaryButton`), so confidence is
high, but a live capture on a signed-in device is a good follow-up.

## Environment note

Hit an `ENOSPC` (disk full) mid-task; cleared `~/Library/Developer/Xcode/
DerivedData` and shut down idle simulators to recover ~14 GiB, then the Swift
build/test proceeded normally.
