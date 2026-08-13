# 2026-08-13 — Profile completion (screens 13, 13A, 16)

## Task

Build the remaining screens that have endpoints, and produce a shareable
write-up covering **only** the backend blockers to finishing registration.

## Outcome

Three more screens shipped. Six blockers documented in a doc scoped to one
question, so it can be acted on without reading the whole handoff.

| Screen | Status |
|---|---|
| 13 — Guided completion checklist | **Built** |
| 13A — Set a password | **Built** |
| 16 — Add emergency contact | **Built**, minus the notify-by control |
| 13B/13C — Common situations | Blocked, no operations |
| 14, 14A–14D — Glovebox | Blocked, no seeded document types |
| 17–21 — Guided tour | Deliberately deferred, see below |

---

## What the schema turned out to allow

| Need | Operation | Verdict |
|---|---|---|
| Set a first password | `setPassword(newPassword:)` → Boolean | ✅ exists |
| Know whether one exists | **`User.hasPassword`** | ✅ exists |
| Emergency contact CRUD | `createEmergencyContact` / `emergencyContactList` / update / delete | ✅ exists |
| Notify-by preference | — | ❌ nothing, schema-wide |
| Glovebox sections | `adminDocumentTypeList` | ⚠️ exists but returns `[]` |
| Situation preferences | — | ❌ nothing |

`User.hasPassword` was the piece that made the checklist honest — without it
"Set a password" would have to be shown to everyone, including people who
already have one.

---

## The Glovebox distinction worth keeping

Screens 14/14A–14D are **not** blocked by missing operations. Everything is
there: `adminDocumentTypeList`, `adminDocumentFieldList`,
`requestUserDocumentUpload`, `createUserDocument`, `userDocumentDownloadUrl`, and
`saveUserDocumentValue` for the plain fields.

The problem is `adminDocumentTypeList` → `[]`. Every upload and every saved value
is keyed by `adminDocumentFieldsId`. No types means no fields means nothing to
attach anything to.

That is a **seeding** ask, not a build ask, and the blockers doc says so — the
distinction changes who has to do the work.

---

## Why the tour (17–21) is not built

It needs no backend at all, so by the letter of "screens that have endpoints" it
qualifies. But all four steps point at things that do not exist in our app yet:
step 2 highlights the Glovebox, step 3 Activity, step 4 the notification bell.

A guided tour of features the member cannot reach is worse than no tour. Deferred
until the Glovebox and Activity land.

---

## Files touched

**`kotlin`** — `Models.kt` (`EmergencyContact`, `hasPassword`), `AsiApi.kt`
(`setPassword`, `listEmergencyContacts`, `createEmergencyContact`),
`AsiComponents.kt` (`AsiRequirementRow`, `AsiChoiceChips`, `AsiChecklistRow`),
`feature/profile/` (new), `MainActivity.kt`, plus
`ProfileCompletionViewModelTest` and `AccessibilityTest`.

**`swift`** — the same structure: `Models.swift`, `AsiApi.swift`,
`AsiComponents.swift`, `Feature/Profile/`, `AttorneyShieldApp.swift`,
`ProfileCompletionViewModelTests`.

---

## Decisions

**The checklist replaced the linear wizard as the post-sign-in landing.** Screen
13 is the design's own hub and it routes to each remaining piece, which is more
faithful than a forced march and gives the wizard a home. A restored session
still goes straight to Home; only a fresh sign-in sees it, and someone with
nothing outstanding never sees it at all.

**Only rows that lead somewhere are shown.** The design lists "Upload documents"
and "Common situations"; both are blocked, so neither row exists. A tappable row
that opens nothing is the placeholder problem in miniature.

**Done rows are not tappable.** They read as finished rather than looking
actionable and doing nothing.

**The percentage rounds down**, so 5 of 6 never displays as 100%.

**The notify-by checkboxes are omitted, not stuffed into `notes`.** `notes` is
free text; using it as a settings column would work right up until something
reads it expecting notes. Sixth blocker in the doc.

**A password needs all three rules *and* a matching confirmation**, and the
mismatch warning only appears once the second field has content — not while
someone is still typing it.

**"Symbol" is deliberately broad** — anything that is not a letter, digit or
whitespace. A member should never be told their password lacks a symbol it
visibly has. Tested with `¿`, `€`, `—`, `_`.

**The first contact saved is marked `isPrimary`.** The design has no control for
it and someone has to be first.

**A contact needs a name plus a phone or an email.** One with neither cannot be
alerted, which is the whole point of the record.

**A failed `hasPassword` read assumes they have one** — the same reasoning as the
PIN check in the setup wizard. Treating "unknown" as "missing" would nag someone
into resetting a password they already set.

**Green is a fill, never text.** The reference says the password checks "flip
green"; Verified Green is 1.62:1 as text on Shield Navy. The green is a filled
dot with a navy tick and the label stays palette text — the same rule a green
status label broke earlier in this project.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **196 pass**, 0 fail (was 175) |
| iOS unit | **197 pass**, 0 fail (was 175) |
| Android instrumented | **30 pass**, 0 fail (was 28) |

New coverage: all three password rules including unusual symbols, save gating on
rules + match, no-mismatch-while-empty, refused password staying on the pane,
percentage rounding, no row for a backendless feature, the failed-lookup
assumption, contact validation, first/last name joining, `isPrimary` only for the
first contact, no bare dial code sent as a phone, and the screen-reader labels for
the drawn ticks.

**One test of mine was wrong, not the code:** I asserted `phoneE164` was absent
from the request body, but the query's own selection set names it. Fixed to
inspect the variables.

---

## Open issues / next steps

1. **Six blockers** are in `notes/registration-blockers.md` — phone verification,
   pronouns, situation preferences, notify-by, Glovebox seeding, incident types.
2. **Who sends the emergency-contact alert?** The design says contacts are
   alerted with the member's location when a call connects. We only call
   `member-call`, so it must be server-side — but nobody has confirmed that, and
   if the app is meant to trigger it we need an operation.
3. **The completion screen has no entry point from Home.** It is reachable after
   a fresh sign-in only. A member who skips it cannot get back without signing
   out, which is wrong — Home needs a "finish your profile" affordance.
4. **`changePassword` is unused.** Members who already have one cannot change it
   in-app yet; the reference puts that in the profile screens (33-series), not
   built.
5. Emergency contacts can be created but not **listed, edited or deleted** in the
   UI. The endpoints exist; the design's management screen is in the 30s.
