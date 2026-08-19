# 2026-08-19 — Profile hub: membership card to the design, and a blocked row

## Task

Bring the Profile hub (screen 33, `AccountScreen`) closer to the CodePen, given
a mockup + current-app screenshot pair. Repos touched: `kotlin`, `swift`,
`asi-claude`.

Three decisions were taken up front: **full membership-card restyle**, **keep
the row sub-captions**, and **add a "Profile & personal info" row** — the last
with the standing rule that a row with no real destination gets reported, not
shipped dead.

## The membership card — full restyle (done)

The card was the biggest gap. Before: a plain "Freedom Basic — Family" title, an
inline green-dot "Covered · 24/7 · You + N" line, and a full-width outlined
"Manage plan" button. The reference (33) is a different shape:

| Element | Reference | Now |
|---|---|---|
| Eyebrow | Gold "PLAN · ACTIVE" | `"<PLAN> · ACTIVE"`, gold caps |
| Headline | "You + 3 members" | the plan composition |
| Coverage | Green "Covered" pill, top-right | pill |
| Renewal + action | "Renews …"  +  gold "Manage plan ›" link | matched |

Data all existed (`planName`, `entitlement.includedSubaccounts`, `family`,
`isCovered`, `isInGrace`) — nothing new fetched.

**Coverage still reads from the entitlement, never the membership status.** That
was the card's original invariant (a membership can say "active" while cover has
lapsed to grace), and it is preserved: both the eyebrow status word *and* the
pill derive from `isCovered` / `isInGrace`, so they cannot contradict each other.

**Two things carried carefully, not dropped:**

- **The pill colour obeys R4.** Verified Green is a fill, never text, so the
  word "Covered" stays in `textPrimary` on a green *tint* — the same pattern as
  the Glovebox "Saved" pill — rather than the CodePen's green text. Grace is a
  gold-tinted pill, "not covered" a neutral one.
- **The grace explanation survives.** The pill only has room for "Grace period",
  so the full "Settle your renewal to keep full coverage." line is kept beneath
  the headline rather than lost to the restyle.

**Fallbacks the mockup doesn't show but the app must handle:** a solo plan has no
member composition, so the plan name becomes the headline and the eyebrow carries
only the status (no duplication); one member reads "You + 1 member"; a family
plan with none added yet reads "You + up to N members" from the seat allowance.

## Row captions — kept

The app's rows carry a caption under each label ("$46.00/mo", "Your Glovebox",
"0 of 2 on your plan"). The CodePen rows are label + chevron only. Kept the
captions on the call taken: the inline info is worth more than the exact match,
and the rows already read cleanly as divided rows from the 2026-08-17 rebuild.

## "Profile & personal info" row — added, with a minimal real pane

The CodePen's Account group opens with a "Profile & personal info" row the app
lacked. Adding the *row* is trivial; the problem was the *destination*.

- The CodePen has **no dedicated personal-info screen** — the only personal-detail
  surface anywhere is the onboarding **Setup** wizard (DOB / gender / pronouns,
  address, PIN).
- `Destination.Setup` always exits via `leaveSetup → Completion` (the checklist),
  not back to Profile.
- Worse, `SetupViewModel.load` treats a member with DOB + address + PIN as
  **already complete** and fires `onAlreadyComplete()` immediately — so a settled
  member (i.e. everyone who reaches the Profile hub) tapping the row would be
  bounced straight out having seen nothing.

So reusing the wizard would have been a no-op for exactly the people who'd tap
the row — a dead control. On the instruction to add the row now and flesh it out
later, I gave it a **real but minimal destination instead**: a new
`AccountPane.Profile` that shows the member's **name and email** (which the
session already holds) as a titled, read-only pane, reached via `onOpen` and
returned from by the hub's existing sub-pane Back.

This keeps the rule intact — the row goes to a real screen, not a lie — while
leaving the **fuller detail (date of birth, address) and editing** as the "later"
work. That still needs product decisions (read-only vs editable; which profile
mutations the API exposes) and, for DOB/address, a `getMyProfile` fetch the
Account view model does not currently make.

Same change on both platforms: `AccountPane.Profile` / `.profile`, the row at the
top of the Account group with the `ic_tab_profile` glyph (present on both), and
the minimal `ProfilePane` / `profilePane`.

## Deliberate deviations left in place (each has a prior reason)

- **Gold icons**, not the CodePen's steel blue — the palette rules blue out; the
  same call taken for the Glovebox.
- **No avatar camera badge** — nothing uploads an avatar (2026-08-17).
- **No back chevron on the tab** — a bottom-nav tab has nowhere to go "back" to;
  consistent with the Glovebox tab and the Activity/Profile rebuild. Sub-panes
  keep their Back.
- **Email under the avatar** — the app keeps it as useful identity; the CodePen
  omits it. Minor, left as-is.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` + `testDebugUnitTest` | **BUILD SUCCESSFUL**, all pass |
| iOS — `AccountViewModelTests` (compiles the changed screen) | **14 / 14 passed**, 0 failed |

No test asserted the card strings being changed (the `planName` assertions live
in the view models, untouched). The card is verified by compile + the existing
view-model suites; the on-device look is the user's to confirm on the signed-in
emulator, which the suites would sign out.

## Next

Profile card is aligned and the personal-info row is in with a minimal pane.
Follow-ups on Profile: **flesh out the personal-info pane** (DOB, address, and
editing — needs a `getMyProfile` fetch and the API's profile mutations). Then the
remaining tab is **Activity (screen 32)**.