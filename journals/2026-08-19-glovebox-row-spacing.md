# 2026-08-19 — Glovebox rows: spacing aligned to the CodePen

## Task

Visual comparison of the Glovebox tab (screen 31) against the CodePen: our rows
read as cluttered and squeezed where the reference's have room to breathe. Align
the spacing. Repos touched: `kotlin`, `swift`, `asi-claude`.

## Why ours was tighter — a scale mismatch, not a value error

The screen was built by porting the CodePen's CSS numbers **1:1 into dp/pt**:
`.gdrow` padding 10, `.gi` tile 32, row gap 7, title→pill 3. Those looked right
against the markup, but the CodePen phones are drawn at a **reduced gallery
scale** — its row title is 11.5px and the subtitle 9.5px, roughly 0.68× a real
phone. So the same absolute numbers that look generous inside a shrunk mockup
render cramped on a device.

Measured against each render's own width (both are full-phone images):

| | CodePen | App (before) |
|---|---|---|
| Row height | 0.175 w | 0.126 w |
| Icon tile | 0.093 w | 0.069 w |

The rows were ~28% shorter and the icon tiles ~26% smaller than the reference,
proportionally. That is the "squeezed" look.

## The change

A small, consistent set of spacing bumps on both platforms. No colour, no logic,
no copy — geometry only.

| Token | Before | After |
|---|---|---|
| Row padding (`.gdrow`) | 10 | 14 |
| Icon tile (`.gi`) | 32 | 40 |
| Icon glyph | 17 | 20 |
| Icon tile radius | 9 | 11 |
| Icon → text gap | 10 | 12 |
| Title → status pill | 3 | 6 |
| Inter-row gap | 7 | 11 |

These restore the reference's proportions (row ≈ 0.17 w, tile ≈ 0.09 w) while
keeping the 12dp card radius and the rest of the header rhythm as they were.
Because the row component is shared, screen 14 (the checklist step) gets the same
breathing room.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — `ScreenRenderTests.screen14RendersTheChecklistStep` | **passed** (render still non-blank) |
| iOS — `AsiIconsTests` (7) | **passed** |

The render tests assert presence and a non-blank frame, not pixels, so a spacing
change does not perturb them — which is what makes them safe to trust here but
also why the *look* still needs an eye. The screenshot that prompted this was a
signed-in Android session, which the suites sign out; the on-device confirmation
that the rows now breathe is the user's to make.

## Related, not done here

- **The tab carries a top "Attorney Shield · Close" lockup** that CodePen screen
  31 does not — the reference tab relies on the bottom nav and has no Close. That
  chrome adds to the density at the top. Left alone: removing it is a navigation
  change, not a spacing one, and screen 14 (which shares the view) does want a
  way back. Worth a separate decision.
- **"attorney" vs "Law Firm Representative"** on the tab subtitle — resolved in
  the addendum below.

---

## Addendum — verbiage matched to the CodePen

Asked to match the wording. Checking the CodePen rather than assuming settled a
surprise: it says **"attorney" 134 times** and **"Law Firm Representative" only
in the Glovebox "shareable with your ___ during a call" subtitle** (screens 14,
30A, 31). So "match the verbiage" is *not* an app-wide attorney→LFR sweep — that
would contradict the reference — it is one contextual string.

The app was internally inconsistent: screen 14 (checklist) already said "Law
Firm Representative", but screen 31 (the tab) still said "attorney" for the same
Glovebox. Aligned the tab subtitle to match both the CodePen and screen 14:

> "Secured · shareable with your ~~attorney~~ **Law Firm Representative** during a call"

One string per platform (`GloveboxScreen.kt` / `.swift`). No test asserted it.
String-only, so no rebuild — a literal cannot change compilation, and the
spacing run already validated these files.

**Left as-is, on purpose — not oversights:**

- The section-detail pill "Encrypted · visible to your **attorney** during
  calls" already matches the CodePen (its 14A pill says "attorney" too).
- The card count **"N of M sections on file"** stays, against the CodePen's
  "4 documents on file". A section holds several fields and only some are files,
  so a document count would disagree with the four rows below it — the deliberate
  correctness call from the Glovebox rebuild.
- The **"ENCRYPTED & READY"** eyebrow stays all-caps against the CodePen's title
  case: that is the design system's Eyebrow-800-caps treatment, applied
  everywhere, not a wording difference.

---

## Addendum 2 — the top bar the CodePen doesn't have

The tab carried a top row — the "Attorney Shield" lockup on the left, a "Close"
on the right — that **CodePen screen 31 has no trace of**. The reference opens
the tab on its "Digital Glovebox" title and relies on the bottom bar; the same is
true of screen 14, which opens on its eyebrow. This is the chrome flagged as
"related, not done" in the spacing entry above.

Removed it. The list panes (tab 31, checklist 14) now open on the title, with no
lockup and no Close.

**Why it was safe to remove the Close, per route:**

- **Tab (`Destination.Glovebox`)** — `TabScaffold` already renders the bottom nav
  for it, so Home/Activity/Profile are one tap away. Close was redundant.
- **Home's "Open your Glovebox" button** — also lands on `Destination.Glovebox`,
  i.e. *with* the bottom nav, so that entry is covered too.
- **Checklist step (`Destination.DocumentsStep`)** — not a tab, so no bottom nav,
  but it has the gold "Done — back to checklist" button plus system back. That is
  exactly what the CodePen screen 14 relies on.

**The one control kept:** the section-detail pane (14A) still needs a way back to
the list, and the CodePen draws a back chevron there. The header used to serve
that with its "Back" text. So the lockup+Close row is gone, and the **detail pane
now renders its own left-aligned "Back"** — a text button, which is the app's
established back idiom everywhere else (Login, Setup, Account, Call, Profile);
there is no chevron asset and adding one is not worth a new palette-guarded
vector on both platforms.

The brand-off-the-tabs decision is not new here — the 2026-08-17 Activity/Profile
rebuild already took the lockup off those tabs "because the reference's tab
screens open on their title, the brand sits on Home." The Glovebox was the last
tab still carrying it; this brings it in line.

**Left wired but unused:** the `onClose` callback (Kotlin `GloveboxCallbacks`,
Swift `GloveboxScreen`) is no longer invoked. Kept with its default rather than
threaded out of `MainActivity` / `AttorneyShieldApp`, to keep the change local;
a harmless dead lambda, noted for a later tidy.

### Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `compileDebugAndroidTestKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — `ScreenRenderTests` + `AsiIconsTests` | **passed** (exit 0) |

The instrumented `ScreenRenderTest` was **compiled but not run** — running it
uninstalls the app and would sign out the emulator the user is building on. Its
source compiles against the changed screen, which is what a no-device check can
prove; the on-device look is the user's to confirm.

## Next

Glovebox tab is aligned (icons, spacing, verbiage, chrome). Per the plan, the
next tab to bring to the reference is **Activity (screen 32)** — rebuilt to the
timeline on 2026-08-17, but not yet re-checked against the CodePen the same way.
