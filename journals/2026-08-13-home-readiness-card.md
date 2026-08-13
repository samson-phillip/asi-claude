# 2026-08-13 — Home's readiness card, and the seeding landing

## Task

Add the "finish profile" entry point on Home — the gap I flagged after building
the checklist, where a member who tapped "Skip for now" could not get back to it
without signing out.

Mid-task the backend asked us to check whether the categories had come through.
They had, and a lot more with them.

---

## The entry point

The reference's screen 27 has a dismissible readiness card:
`✕ 80% Protection readiness / Add emergency contacts to be fully ready ›`. That
is the entry point, so that is what was built — it **names the specific next
step** rather than nudging generically, so a member knows what tapping it will
ask of them.

Verified on a device: Home shows *"83% PROTECTION READINESS / Set a security PIN
to be fully ready ›"*, and tapping it opens the checklist.

### The refactor it forced

Home and the checklist both need the same readiness figures. Computing them twice
would eventually produce "80% on Home, 66% on the checklist", so the model and its
loader moved into `core/profile/ProfileReadiness` and both screens now read the
same thing. That is the whole reason the shape exists.

---

## Decisions

**The card is not gold-filled.** Gold belongs to the attorney button, and the
CodePen's own rule is one job per screen with that button always the hero. The
card is a bordered surface with a gold accent, so it reads as secondary to the
thing that reaches a lawyer.

**Dismissal is not persisted.** The reference makes it dismissible; we hide it for
the session only. Persisting it would mean one tap of the cross and the member is
never reminded again about an incomplete profile.

**Readiness loads separately from the tiles and can never fail the screen.** Four
reads for a decorative card must not stand between a member and the attorney
button.

**Home refreshes readiness on every entry, not just on creation.** The view model
outlives navigation, so after finishing a checklist item the card would otherwise
still show the percentage from sign-in. `refreshReadiness()` is deliberately
separate from `load()` so returning to Home does not re-fetch the tiles.

---

## A design flaw my own test caught

The first version showed the card whenever anything was outstanding. A test that
failed all four readiness reads then produced:

> **50% Protection readiness — Add your personal details**

That is a **fabricated percentage from a failed read**, and it would send someone
to redo work they had already done. The rule "an unknown state is never treated as
missing" was already applied to the PIN and password checks; it was not applied to
the profile read.

Fixed: a failed profile read marks those rows satisfied rather than missing, and
the card stays hidden. The test now asserts the specific thing that matters —
nothing already done may be reported as outstanding.

One imprecision left deliberately: `listEmergencyContacts` never throws, so a
failed read is indistinguishable from having none. The cost is a single nudge that
corrects itself on the next successful load, which is why it is left alone and
documented rather than papered over.

---

## The seeding landed — and it exposed a bug in our code

Checked on request. Everything came through:

| Check | Result |
|---|---|
| `countries` | **United States** |
| `adminIncidentTypeList(activeOnly: true, countryISO2: "US")` | **6 types**, exactly the design's set |
| `adminLanguageList` | **`en-US`, `isDefault: true`** + `es-ES` + `ar-SA` |
| Translations | English **and Spanish** on every type |
| `iconFilePath` | Real CloudFront URLs on all six |
| `adminDocumentTypeList` | **All four Glovebox sections** + 20 fields |

So A1, A2 (the only BLOCKING item) and A3 are all resolved.

### The bug

**The seeded `code` values are human strings — `"Traffic Stop"`, not
`traffic_stop`.** Our emoji map keyed on snake_case, so it matched nothing and
**every one of the six tiles fell back to the generic shield.**

This is a bug that could only appear once the data existed: with an empty list
there was nothing to mis-key. Fixed by normalising the lookup (lowercase,
whitespace and hyphens to underscores), with a regression test naming the real
codes, and a test that the old snake_case form still resolves.

Verified by eye on a device — all six tiles now carry the right emoji.

---

## Files touched

**`kotlin`** — `core/profile/ProfileReadiness.kt` (new), `core/network/AsiConfig.kt`
(icon normalisation), `feature/home/HomeViewModel.kt` + `HomeScreen.kt`
(readiness card), `feature/profile/*` (moved onto the shared model),
`MainActivity.kt`, plus `HomeViewModelTest` and `AsiApiTest`.

**`swift`** — `Core/Profile/ProfileReadiness.swift` (new), `Core/Network/AsiConfig.swift`,
`Feature/Home/*`, `Feature/Profile/*`, `AttorneyShieldApp.swift`,
`HomeViewModelTests`.

---

## Test results

| Suite | Result |
|---|---|
| Android unit | **205 pass**, 0 fail (was 196) |
| iOS unit | **202 pass**, 0 fail (was 197) |

**Two existing tests legitimately broke** — one on each platform, both the same
one: `T-H-5` asserted a total request count of 1, and Home now also reads
readiness. The intent was "no roster query without a partner", so both now assert
that specifically. Counting total requests breaks every time a screen
legitimately asks for something new.

### Verified on device

Signed in on the emulator against dev and walked the whole path:

- The checklist showed **83% COMPLETE** with real ticks and "Security PIN — Add"
  outstanding
- Home showed **six real incident tiles** with correct English names and correct
  per-type emoji
- The readiness card read **"83% PROTECTION READINESS / Set a security PIN to be
  fully ready"**
- Tapping the card opened the checklist

---

## Open issues / next steps

1. **The Glovebox is now unblocked** — screens 14, 14A–14D. All four sections and
   20 fields are seeded, and the upload pattern is
   `requestUserDocumentUpload` → S3 → `createUserDocument`. This is the obvious
   next build.
2. **`iconFilePath` now has real URLs and we still render emoji.** No image loader
   is wired on either platform. Android needs a dependency (Coil); iOS has
   `AsyncImage` built in. Ours to do, not a backend ask.
3. **`adminDocumentTypeList` contains test rows** — `"contract 2"`, `"Extra
   books"` — alongside the real sections. We will render only the four Glovebox
   sections; worth them tidying dev.
4. **Still open on the backend:** a case for the test member (A4), phone
   verification, pronouns, situation preferences, emergency-contact notify-by,
   trial/guest, and the eight answers in §C.
5. **A real video call still has never connected.** `member-call` returns `409`
   with no attorney online.
6. **The dev machine is at 6.7 GiB free** and the emulator died twice during this
   task, costing a couple of test runs.
