# 2026-09-01 — Hide the common-situations picker (CEO directive)

## Directive

Innocent relayed a CEO directive: remove the member's ability to selectively
add/remove incident types on Home — Home should **always show all incident types**
in the admin's order, matching `member-client`. Confirmed against the web
reference: `member-client/src/lib/homePrefs.ts` quotes the CEO ("Maintain regular
incident type buttons… Do not implement any new functionality around incident
buttons being configured by the user. These will remain configured and
order-sorted by the admin") and the web removed the picker entirely.

## Approach — hide, don't delete

Per the user: keep the code (they may re-enable it) but **hide** the feature from
Home and registration. So a single feature flag, default **off**, gated at the
source. The `Situations` screens/VMs and the `getCommonSituations` /
`setCommonSituations` API stay in the tree, just unreachable.

- New `FeatureFlags.situationsPickerEnabled` / `SITUATIONS_PICKER_ENABLED` (both
  platforms), default `false`. A `var` (not `const`/`let`) only so tests can turn
  it on; production never writes it.

Gated three source points per platform (incident types are already fetched with
`sortOrder` and sorted, so "show all in admin order" needed no new ordering):

1. **`ProfileReadiness.loadProfileReadiness`** — `includeSituations` param
   (defaults to the flag). When off: skip `getCommonSituations`, don't add the
   "Your common situations" task. This removes it from the registration checklist,
   from the readiness **percentage** (so a member isn't stuck below 100% on a
   hidden task), and from Home's chosen-subset (empty `situationIds` →
   `hasChosenSituations` false → Home renders the full `IncidentGrid`).
2. **`NudgePolicy.pick`** — `includeSituations` param; excludes `.situations` from
   the nudge candidates (needed because `isDone` reads an absent task as "not
   done", so the nudge would otherwise still fire).
3. **Home screen** — hide the "Change / Choose" button.

## Tests

The view-model tests drive the *real* `loadProfileReadiness` (StubURLProtocol on
iOS, MockWebServer on Android) and assert readiness **including** situations, so
they'd break with the feature off. Rather than rewrite their expected
percentages/rows, the two affected suites (`HomeViewModel*`, `ProfileCompletion*`)
now flip the flag **on** in setup — they legitimately test the feature, which
still exists. `ProfileReadiness*`/`NudgePolicy*` build their readiness directly and
were unaffected.

Also fixed a **pre-existing** stale test on Android (unrelated to this change):
`AsiApiTest` expected a member-call **403** to be `UnauthorizedException`, but the
sanctions work made 403 → `SanctionedException` (401 is the rejected-token case).
Corrected it and added the 403 → `SanctionedException` coverage — the same fix
already applied to iOS earlier this session.

- iOS `AttorneyShieldTests` **TEST SUCCEEDED**; Android `testDebugUnitTest`
  **BUILD SUCCESSFUL**.

## Re-enabling later

Flip the one flag to `true` on each platform and rebuild — the picker, its
onboarding step, its nudge, and Home's chosen-subset all come back. Nothing was
deleted.

## Files

- Swift: `Core/FeatureFlags.swift` (new), `Core/Profile/ProfileReadiness.swift`,
  `Core/Nudge/NudgePolicy.swift`, `Feature/Home/HomeScreen.swift`, + test-suite
  setup in `HomeViewModelTests`, `ProfileCompletionViewModelTests`.
- Kotlin: `core/FeatureFlags.kt` (new), `core/profile/ProfileReadiness.kt`,
  `core/nudge/NudgePolicy.kt`, `feature/home/HomeScreen.kt`, + test setup in
  `HomeViewModelTest`, `ProfileCompletionViewModelTest`, and the `AsiApiTest` fix.
