# 2026-08-17 — Glovebox rebuilt to the design

## Task

Continue the UI polish pass: bring the Glovebox list (screen 31) and the open
document section (14A) to the reference, and apply its assets.

## The list — screen 31

| Element | Reference | Was | Now |
|---|---|---|---|
| Heading | "Digital Glovebox" + one-line subtitle | "Your Glovebox" + a paragraph | Matching |
| Hero | `.gvcard` — gold eyebrow, count, watermark padlock | An `AsiInfoChip` of prose | Card |
| Rows | 32px icon tile, name, status pill, View/Add | Card, emoji tile, "View ›" | Matching |
| Section icons | One glyph per section | **One emoji folder for all four** | Four glyphs |

The icons were the substance. `icon` holds a CloudFront URL for three of the
four sections and the literal string `"globe"` for the fourth; nothing fetches
those, so every section fell back to the same emoji and the four tiles were
indistinguishable. The **code** now picks the glyph, and the admin field is
ignored until an image loader exists to honour it.

## The section — screen 14A

- The "Encrypted · visible to your attorney" line becomes the green pill with a
  lock.
- Document tiles gain the gold-edged thumbnail well, tighter type, and the
  red-tinted remove.
- The upload control becomes the dashed gold "+ Add another document".

**One thing deliberately not copied.** The reference pairs that control with
separate **Camera** and **Gallery** buttons. Nothing in either app captures from
the camera — Android launches `GetContent`, which already offers gallery *and*
files. A Camera button would open the same picker under a false label, so there
is one honest control instead of two until capture is built. Same reasoning that
kept the per-tile delete out while `deleteUserDocument` returned `forbidden`.

## Colour

Gold stands in for the reference's steel blue `#2E78C8` throughout, on the
ruling given today. It is used on every row's icon tile here, not just a link or
two as on Home, so the screen reads noticeably more gold than the mockup — worth
seeing before it is taken as settled.

The remove uses **Live Red**, the palette's single red, as a *tint* rather than a
label colour. It exists for the call screen's on-air badge; this is the only
other place it appears.

## Two faults the render caught that the diff did not

- **The watermark was sizing the card.** Given a plain size it became the tallest
  child and left a band of empty space under the copy. Laid out with
  `matchParentSize` so it cannot.
- **The two counts contradicted each other** — "2 sections on file" and "3 still
  to add" across four sections, because a part-filled section is both. It reads
  "2 of 4 sections on file" and says it once.

## A process fault that cost real work

**I destroyed the signed-in emulator session twice.** `connectedDebugAndroidTest`
uninstalls the app in its teardown, and I was using it to render screens for
screenshots — so every capture run signed the device out. The second time the
session had a real account with three situations saved.

Rendering through an instrumented test is fine on a signed-out device and the
wrong tool on a signed-in one. **Drive the live app for visual checks** unless
the screen is unreachable without state we cannot produce.

Two smaller traps in the same loop: a "non-background pixels" detector matched
the launcher wallpaper, and a "dark background" detector matched a blank navy
screen mid-launch. A useful detector needs both — the app's own background *and*
enough content to prove it drew.

## Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **421 / 421**, 0 failed |

## Next on the polish pass

Done: Home, finish-setup checklist, tab bar, incident tiles, Glovebox list and
section.

Remaining, in the order a member meets them: **Activity** (32), **Profile** (33)
and its sub-screens (33A–33D), the **call** surfaces (28–30A), **notifications**
(24–26), and the **situations picker** (13C).

---

## Addendum — Activity rebuilt to the design (screen 32)

| Element | Reference | Was | Now |
|---|---|---|---|
| Structure | One rail, dots straddling it, text alongside | A stack of bordered cards, dot inside each | Rail |
| Header | Title only | Lockup + title + standfirst | Title only |
| Dots | 15px, ringed in the page colour, glyph inside | 10–12px plain circles | Ringed, with a glyph |

The lockup and standfirst went with it: the reference's tab screens open on
their title, the brand sits on Home, and the tab bar is the navigation. Applies
to the Glovebox and Profile too — the Glovebox keeps its header only because it
is also reachable from Home's button and needs the Close.

**The dots keep our meaning, not the reference's.** It varies them by event
*kind* (call, test, joined); ours vary by **outcome**, so a member scanning the
rail can see which sessions actually connected. Green and gold stay fills with
the glyph on top — navy on gold, white on green — because neither is legible as
text on navy.

**"View transcript ›" is not built.** Nothing exposes a transcript, and a link
that goes nowhere is worse than no link. Same rule as the Camera button and the
delete control before it.

### The rail exposed the same fault twice in one day

`fillMaxHeight` inside a `verticalScroll` has an infinite constraint, so the rail
drew nothing at all — the dots rendered and the line between them was simply
absent. Fixed the same way as the Glovebox watermark: fill a box that takes the
*parent's resolved* height, which the rows determine.

Worth generalising: **a child cannot size itself to a parent whose height is
still being decided by that same child's siblings.** Both times the symptom was
silent — no error, just a missing element in the render.

### Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **421 / 421**, 0 failed |

### Remaining on the polish pass

**Profile** (33) and its sub-screens (33A–33D), the **call** surfaces (28–30A),
**notifications** (24–26), the **situations picker** (13C).

---

## Addendum — Profile hub rebuilt to the design (screen 33)

| Element | Reference | Was | Now |
|---|---|---|---|
| Header | Name centred over an avatar | Lockup, then name left-aligned | Centred over an avatar |
| Rows | `.mrow` — glyph, label, chevron, hairline | Bordered cards with "Open"/"Manage" | Divided rows |
| Groups | Account / Protection / More | Same | Same |

`AsiNavRow` **gained** the variant rather than changing: sixteen call sites use
it, and a sub-pane's rows are separate objects that still want their borders.
The hub is one list of destinations and now reads as one.

**The avatar's camera badge is left off.** The reference puts a gold camera on
the avatar for changing the picture; nothing uploads an avatar. Same call as the
Camera button on the document section, and the delete control before that — the
rule holds across four screens now.

### Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **421 / 421**, 0 failed |

### The capture loop, third variant

The frame detector rejected the right screen twice more: once because the upper
bound on "non-background pixels" was tuned to the Activity timeline (sparse) and
the Profile hub is dense, once because the fixture failed to compile and the run
never reached the screen at all. Both cost a full build cycle.

The lesson is not to tune thresholds per screen. **Detect the app by a stable
property** — its background at two known points — and treat pixel counts as a
lower bound only.

### Remaining on the polish pass

The Profile **sub-screens** (33A payment & plan, 33B family, 33C settings, 33D
payment method) are unchanged — they use the card form deliberately. The **call**
surfaces (28–30A), **notifications** (24–26) and the **situations picker** (13C)
are still to do.

---

## Addendum — a parity check, and what it caught

Asked whether the polish was going to both platforms. It was: nine paired
commits today, same order, same subjects, on `kotlin/dev` and `swift/main`. The
only single-platform commit is the iOS Keychain reset, which Android does not
need (`allowBackup="false"`, and app data goes with the uninstall).

But comparing the two **asset sets** rather than the commit subjects found a
real defect.

### The join dot was invisible on iOS

`ActivityScreen` asked for `Image("ic_check")` and no such asset existed, so the
join-event dot on the timeline rendered nothing at all.

**Nothing caught it.** `Image` with an unknown name is not a compile error and
not a crash — SwiftUI draws nothing — so the build succeeded and all 421 tests
passed. Android was verified by looking at the render; iOS only by build and
tests. That is precisely the gap, and it is the second time today that a missing
element was silent (the timeline rail was the first).

`AssetCatalogTests` now walks the source for `Image("...")` literals — plain and
ternary forms — and fails on any name with no imageset behind it. Confirmed both
ways: it fails when the name is broken, passes when it is not.

### The rest of the drift, and why it is fine

| Asset | State | Verdict |
|---|---|---|
| `ic_bell` | Android only | iOS uses the SF Symbol `bell` — platform-native, deliberate |
| `ic_brand_shield` / `brand_shield_hero` | Same mark, different names | Naming drift only; both render |
| `ic_incident_car`, `_pedestrian`, `_questioned` | Android only | The orphans already flagged for deletion |
| `ic_row_support` | Android only, unused | Authored for a row we do not build. **Deleted.** |

### Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| iOS unit | **422 / 422**, 0 failed (+1: the asset guard) |

---

## Addendum — screen 14 was a missing screen, not a restyle

Shown the CodePen's Glovebox and asked to match it. The screenshot was **screen
14, "Upload documents"** — the checklist's step — not screen 31, the Glovebox
tab I had rebuilt. They share their content and differ in frame.

**What the app did:** tapping "Upload your documents" on the checklist navigated
to the Glovebox **tab**. Same sections, but framed as a destination rather than
a task: a tab bar, and no way back to the checklist the member came from.

**What it does now:** a `DocumentsStep` destination renders the same screen with
a "Finish your profile" eyebrow, its own title and subtitle, a card counting
what is left ("2 more documents to add"), and "Done — back to checklist". One
flag on the existing screen, not a second copy — the section editor beneath is
untouched.

The row style needed no change: the reference's `.gdrow` is a bordered card at
radius 12 with 10px padding, which is what the Glovebox rebuild already
produced. Worth noting because the flat/divided treatment used on the *profile
hub* would have been wrong here.

### The checkbox is not built

Screen 14 carries "Mark documents as complete". Nothing in the schema stores a
per-step completion: `completeMyOnboarding` finishes onboarding as a whole, and
readiness is derived from whether documents exist. A member who ticked it would
find the step un-ticked on the next load. Recorded as backend-gaps question 8 —
either the checkbox is wrong for a derived step, or a flag needs to exist.

That is the fifth control left out for want of a backend, after the delete, the
Camera button, the avatar camera badge and "View transcript ›".

### An operational note

The machine ran out of disk mid-run — `checkDebugAarMetadata` failed with "no
space left on device". My own screenshot frames were **160 MB** of it, now
cleared. The volume is still at 417 GiB of 460 GiB with under a gigabyte free,
which is not something this session created but will keep breaking builds.
Sampling frames are now deleted as soon as the useful one is found.

### Tests

| Suite | Result |
|---|---|
| Android unit | **433 / 433**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **422 / 422**, 0 failed |
