# 2026-08-14 — Unblock the instrumented suite: `AccessibilityTest` → current readiness API

## Task

Close the open issue left by
[`2026-08-14-current-location-routing.md`](2026-08-14-current-location-routing.md):
the whole `androidTest` source set failed to compile because
`AccessibilityTest.kt` still referenced a removed readiness API — `CompletionItem`,
`CompletionItemId`, and a `ProfileCompletionScreen(items = …)` parameter. That one
stale file made `compileDebugAndroidTestKotlin` fail, which blocked **every**
`connectedDebugAndroidTest` run — the instrumented suite was red on `main`.

Goal: update the test to the current API, get `compileDebugAndroidTestKotlin`
green, and prove the on-device suite runs again.

## The rename that happened underneath the test

The completion checklist model moved out of `feature/profile` and into
`core/profile`, and its shape changed so Home's readiness card and the checklist
share one source of truth ([`ProfileReadiness.kt`](../kotlin/app/src/main/java/com/attorneyshield/member/core/profile/ProfileReadiness.kt)):

| Old (removed)                                  | Current                                                              |
| ---------------------------------------------- | ------------------------------------------------------------------- |
| `CompletionItem(id, label, done)`              | `ProfileTask(step, label, done, callToAction)`                      |
| `CompletionItemId.Account` / `.Password`       | `ProfileStep.Account` / `.Password`                                 |
| `ProfileCompletionScreen(state = …items = …)`  | `CompletionUiState(readiness = ProfileReadiness(tasks = …))`        |

`CompletionUiState` still exposes a derived `items: List<ProfileTask>` (it just
reads `readiness.tasks`), and the checklist row semantics are unchanged — so the
content-description assertions the test makes did not need to move.

## What changed in the test

`app/src/androidTest/java/com/attorneyshield/member/feature/AccessibilityTest.kt`:

- Imports: dropped `feature.profile.CompletionItem` / `CompletionItemId`; added
  `core.profile.ProfileReadiness`, `ProfileStep`, `ProfileTask`.
- Both call sites (`theCompletionScreenAnnouncesItsStateNotJustItsShapes`,
  `theChecklistAnnouncesDoneAndOutstandingRows`) now build
  `readiness = ProfileReadiness(tasks = listOf(ProfileTask(ProfileStep.Account,
  "Account created", true, "Create your account"), ProfileTask(ProfileStep.Password,
  "Set a password", false, "Set a password")))` instead of `items = listOf(...)`.

### Decision: keep the same two rows (Account done, Password not) — the assertions depend on it

The checklist test asserts the exact spoken labels and the progress percentage,
so the test data is load-bearing, not arbitrary:

- `AsiChecklistRow` announces `"$label, done"` and `"$label, not done. $actionLabel"`
  (actionLabel = "Add" in the checklist pane) → the test's expected
  `"Account created, done"` and `"Set a password, not done. Add"` are exactly one
  done row and one outstanding row.
- `ProfileReadiness.percent` is `donecount * 100 / size` → **1 of 2 done = 50%**,
  matching the expected `"50 percent complete"`.

The `callToAction` strings are required by `ProfileTask` but never asserted here,
so they just mirror the production loader's wording for the same two steps.

## Files

- **kotlin** (test only, no production change):
  `app/src/androidTest/java/com/attorneyshield/member/feature/AccessibilityTest.kt`.

## API

None. Pure test-compilation fix — no endpoints, no request bodies, no
production code touched.

## Tests

- `./gradlew compileDebugAndroidTestKotlin` — **BUILD SUCCESSFUL** (was failing to
  compile; this was the whole blocker).
- `./gradlew connectedDebugAndroidTest` on the connected **Infinix X6886 (Android
  15)** — **30 / 30 passed, 0 skipped, 0 failed**. The instrumented suite is
  runnable on a device again, including the two `AccessibilityTest` cases that
  were touched.

## Open issues / next steps

- None outstanding for this fix. The "instrumented suite red on `main`" item from
  [`2026-08-14-current-location-routing.md`](2026-08-14-current-location-routing.md)
  is now **resolved**.
