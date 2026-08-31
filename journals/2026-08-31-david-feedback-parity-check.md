# 2026-08-31 — David's testing-feedback parity check

## Task

Third parity pass. member-client commit `1d5e240` ("David's testing feedback:
checkout copy, settings, names, addresses, outcomes") lists 16 items from the
2026-08-31 testing doc. Mapped each to the mobile apps (an Explore agent + direct
reads) and implemented the ones that genuinely apply.

## Per-item disposition

| # | Item | Mobile disposition |
|---|---|---|
| 1.1 | Promo code label | **N/A** — no in-app checkout (members go to web). |
| 1.2 | Consent "per mo" → "per month" | **Already correct** — mobile's charge copy is prose and its cadence line spells the period out ("billed monthly"). Covered in the money pass. |
| 2.1 | PIN reveal on every PIN field | **N/A** — mobile enters PINs on a numeric **keypad with dots** (`AsiPinPad`), not a masked text field, so there is no text to unmask. |
| 2.2–2.4 | 2-primary emergency-contact cap + message | **N/A** — mobile has no member-facing "make primary" toggle (the first contact added is auto-primary; "the design has no control"), so there is no third-primary to refuse. No cap UI to attach to. |
| 2.5 | "Payment and Plan" → **"Plan Details"** | **DONE** — renamed the pane title, the Account menu row, and the delete-account footnote on both platforms. |
| 2.6 | Plan-inclusions row → "What's Included" | **N/A** — no plan-inclusions/benefits screen on mobile. |
| 2.7 | Remove "Delete Account" from the UI | **NOT mirrored — deliberately.** Removing in-app account deletion from the **native** apps would violate **App Store Guideline 5.1.1(v)** and Google Play's account-deletion policy (both require in-app deletion when the app supports account creation, which these do). The web app has no such rule. Mobile **keeps** Delete Account. ⚠️ flagged. |
| 2.8 | "Terms of Use" → "Terms of Service" | **Already correct** on both platforms. |
| 2.9 | Law-firm terms → "Law Firm Terms of Service" | **Already effectively there** — mobile uses one combined "Terms of Service" link (Attorney Shield + Law Firm), already the right words; the two-link web structure is a deliberate mobile simplification. |
| 2.10 | First name / Last name as separate fields | **DONE** — see below. |
| 2.11 | Address "Label" → "Search Address" | **N/A** — mobile's "Label" is the address **nickname** field (placeholder "Home, Work…"), not a Places search box. Belongs to the deferred address-autocomplete theme. |
| 2.12 | Google address autocomplete | **Deferred** — its own theme; needs native Places (Android Places SDK / iOS MapKit), not a port. |
| 2.13 | Current Location behind a flag | **N/A** — no Current Location feature on mobile. |
| 2.14 | Outcome tags Canceled/Missed/PIN-Ended/LFR-Ended + timestamp fallback | **Not mirrored — design divergence.** Mobile's Activity deliberately shows **no label** for a completed call ("its duration already says it happened") and friendly wording for the rest ("No attorney answered"), so it never exhibits David's bug (the web list inventing "Requested"/"Connected"). Adopting the terse business chips would be a redesign of the timeline, not a fix. Flagged for a design call, not imposed. |

## Item 1 — "Plan Details" rename

`"Payment & plan"` → `"Plan Details"` in the pane title + Account row, and the
"Delete account lives in …" footnote updated to match. Both platforms.

## Item 10 — First / Last name

Mobile edited the name as a single **"Full name"** field bound to the one stored
`displayName`. member-client (2.10) splits it into First + Last. Mirrored:

- New shared helper `PersonName` (`splitName` / `joinName`), a direct port of
  member-client's `personName.ts` — split on the **first** space (so compound
  surnames survive and a one-word name keeps its first name), rejoin verbatim for
  storage. The split of an existing single string is an editable guess; what the
  member types round-trips stably.
- `AccountViewModel`: `profileName` → `profileFirstName` + `profileLastName`;
  seeded via `splitName(displayName)` on load and on the `getMe` refresh; saved via
  `joinName(...)` back into the single `displayName`. `canSaveProfile` now checks
  the joined name.
- `AccountScreen`: one field → two ("First name" / "Last name"). Kotlin threaded
  the two setters through the callbacks object + `MainActivity`.

The backend still stores only `displayName`; storing the halves separately is a
bigger change (migration + gateway + clients) — same call member-client made.

## Files

- Swift: `Feature/Account/AccountScreen.swift`, `Feature/Account/AccountViewModel.swift`,
  new `Core/Format/PersonName.swift`; tests `AccountViewModelTests.swift`, new
  `PersonNameTests.swift`.
- Kotlin: `feature/account/AccountScreen.kt`, `AccountViewModel.kt`, `MainActivity.kt`,
  new `core/format/PersonName.kt`; tests `AccountViewModelTest.kt`, new `PersonNameTest.kt`.

## Tests

- Swift: `-only-testing:PersonNameTests -only-testing:AccountViewModelTests`
  (single-process, iPhone 16 Pro) → **43 tests passed**, `** TEST SUCCEEDED **`.
- Kotlin: `PersonNameTest` + `AccountViewModelTest` → **BUILD SUCCESSFUL**.

Committed to `dev` on both repos.

## Open decisions for the team

- **2.7 (Delete Account):** kept on mobile for store compliance — confirm that is
  the intent (web removed it; native cannot).
- **2.14 (outcome tags):** whether to bring the four business tags
  (PIN-Ended / LFR-Ended) into mobile's Activity timeline, which today shows a
  duration and no chip for completed calls.
