# 2026-08-16 — Welcome screens 4 & 5 to the client mockups, and the screen 2 tile clipping

## Task

Three things, from the same session as the screen 3 constellation:

1. **Fix the screen 2 tile clipping** I found in passing at 360dp.
2. **Build screens 4 and 5** to the mockups the business side sent.
3. A message from the backend engineer about guest users — see the last section;
   it is not code and it is not done.

## Screen 2 — the clipping

At 411dp the tiles were fine. At 360dp on a short stage a fixed 44dp icon chip
plus a 15sp label was taller than the row, and the longer labels were cut off
mid-glyph ("Traffic accident", "All law enforcement-initiated encounters").

The chip, padding and both label sizes are now derived from the tile itself
inside a `BoxWithConstraints` / `GeometryReader`. One extra wrinkle: at the first
size that fitted, the scope tile broke **mid-word** — "enforcement-initiate / d
encounters" — because its single longest word was wider than the line. Its size
is now clamped a step lower so the word always fits.

## Screen 4 — the orbiting tool carousel

The old screen 4 was a stacked card deck with a progress row. The mockup is
something else entirely: four tool cards riding a dashed orbit ring around a
focus panel.

Read from the reference rather than inferred (`.tools-carousel`, CSS 6403–6632,
JS 14667–14713):

- `position = (index - activeTool + 4) % 4`, and the four slots are **top**
  (scale 1.1, z 5, gold border), **right** at `left:82%` (0.83, opacity .68),
  **foot** (0.83, .56) and **left** at `left:18%` (0.83, .68).
- Rotation every **3800ms**, travel **720ms** on `cubic-bezier(.22,.75,.25,1)`,
  and the focus panel dims to `.64`/`scale .97` while turning, restoring at
  **760ms** when the new top card becomes active.
- Ring: 69% of the art width, 1px dashed gold `.34`, an inner hairline inset 9%,
  and a lit gold hub.

Because a card only ever advances **one** slot, the straight-line interpolation
the reference uses never cuts across the ring — so no arc maths was needed.

The card labels are deliberately terser than the panel titles, which is the
reference's own split ("Cloud recording" on the card, "Secure cloud recording" in
the panel). The four tool icons already existed from the 2026-08-15 vector pass.

**Not reproduced:** the reference gives each icon its own keyframes (the cloud
floats, the GPS rings expand, the lock pulses, the folder papers lift) and runs
them only on the top card. That is four bespoke animations for a marketing hero;
this takes the shared part — the active icon scales to 1.08 and gains its gold
glow — and leaves the per-icon motion out.

## Screen 5 — the Member Protection Warranty illustration

The first hero on a **light** stage other than screen 2, so `stageIsDark` and
`stageColor` now treat Warranty like IncidentTiles and the wordmark plus status
bar flip to navy. Its stage (`.hero-five`) is a cream that deepens toward the
foot with a gold wash low-left and a green one high-right; `drawStage` /
`StageBackdrop` gained a second layered case for it.

Three cards, all the reference's: an outcome card with a navy scales tile, the
`$150.00 reimbursement` / `Approved` copy and a breathing green check, under a
3px navy→gold→green rule; a centred amount card; and the clarifier strip, which
reuses the already-tested `WARRANTY_DISCLAIMER` wording.

**The scales mark.** The reference uses the `⚖` emoji. Android gets a new
`ic_mpw_scales.xml`; SF Symbols has no balance scales (`scalemass` renders a
kettlebell, which I only caught by looking at the simulator), so iOS traces the
**same 24-unit geometry** as a SwiftUI `Shape`. Both platforms now show the same
mark.

## Colour decisions, both against the mockup

Two places where the mockup uses a value the palette forbids, resolved the same
way as the sheet eyebrow and flagged again:

- **"MEMBER PROTECTION WARRANTY"** is gold in the mockup. Justice Gold on white
  is **3.13:1** and fails AA for text that size, so it stays navy.
- **The outcome card's eyebrow** is a mid blue (`--asc-blue #0d3c66`) the palette
  has no equivalent for; Shield Navy stands in.

## Files

- **kotlin**: `WelcomeHeroes.kt` (screen 2 tile sizing; `ProtectionToolsHero`,
  `OrbitRing`, `ToolOrbitCard`, `ToolFocusPanel`; `WarrantyHero`, `OutcomeCard`,
  `ApprovedCheck`, `AmountCard`, `ClarifierStrip`; shared `relSp`),
  `WelcomeScreen.kt` (light stage for Warranty, `drawWarrantyStage`, routing),
  `res/drawable/ic_mpw_scales.xml`, `ic_mpw_check.xml`.
- **swift**: `WelcomeHeroes.swift` (same set plus `ScalesMark`),
  `WelcomeScreen.swift` (`StageBackdrop` warranty layer, routing).

No palette values added.

## Tests

| Suite | Result |
|---|---|
| Android unit | **429 / 429**, 0 failed |
| Android instrumented | **30 / 30**, 0 failed |
| iOS unit | **411 / 411**, 0 failed |

Verified by eye on the **Pixel 8a emulator (411dp)**, at a forced **360dp**, and
on the **iPhone 16 Pro** simulator. Two layout bugs were caught only by the
360dp pass and fixed: screen 4's foot card hung below the sheet because slots
were computed from a *nominal* 23% card height rather than the real one, and the
iOS orbit labels truncated ("Cloud reco…") instead of wrapping.

## Open issues / next steps

- **Screen 6 still has no mockup** — it keeps the code-drawn US map.
- **The gold-eyebrow question has now come up three times** (screens 3, 4, 5).
  Worth one ruling from Blue Sky rather than a note per screen.
- Still open from earlier today: the **blue stage lift on screen 3** has no
  palette equivalent, and the **sheet body copy clips mid-glyph** on short
  screens (it scrolls, so the text is reachable, but it reads as broken).

## Backend: guest users — NOT started, and one blocker

The backend engineer's message, verbatim: *"i have added guest user
implementation. you can sign up with a new account and test it in member
client"*.

**I have not tested it, and I cannot do the part as described.** Signing up
creates an account and enters credentials, which I do not do. That one needs
you — or an existing test account handed to me.

What I *can* do without an account, and would suggest next:

1. Read what the gateway now exposes for guests (`member-client/src/lib/api.ts`
   plus a schema introspection) and write the delta into `notes/backend-gaps.md`.
2. Say concretely whether it unblocks the guest path in development plan §3,
   which is currently listed as having no backend at all.

Worth knowing: this is potentially significant for scope. §3 records the CodePen
journey (sign-up / payment / trial / **guest**) as blocked rather than merely
unbuilt, so if guest is now real, part of that unblocks.
