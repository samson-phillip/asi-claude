# 2026-08-16 — Welcome screen 3 rebuilt to the client mockup: the credential constellation

## Task

The business side shared the mockup for **welcome screen 3** ("Meet Your Legal
First Responder") — the attorney portrait at the centre of six credential cards,
joined by **animated dashed lines**. Rebuild it on both platforms, taking the
images, SVGs, colours and feel from `code_pen_design.html`.

Screens 1 and 2 were delivered on 2026-08-15; this is the third of six.

## Getting the reference's real values (read, not guessed)

`code_pen_design.html` carries the whole thing under `.lfr-experience-map`
(markup ~line 8085, CSS 5983–6226). Everything below is read from that source:

- **The portrait** is a base64 JPEG on `.lfr-portrait-card > img` — extracted
  (389×820, 34 KB) and bundled. It is a **different asset** from screen 1's hero
  photo (547×820), confirmed by hash.
- **Geometry**, all as percentages of the art box: cards 28.5% wide with
  `min-height: 18%`, pinned `left:0` / `right:0` and `top:0` / `top:40.5%` /
  `bottom:0`; portrait 35% wide spanning `top:21%`..`bottom:18%`.
- **Connector net**: `viewBox 0 0 100 100`, `preserveAspectRatio="none"`, centre
  (50,49), endpoints (15,11) (85,11) (14,50) (86,50) (15,89) (85,89) — which are
  exactly the card centres. Stroke `rgba(242,170,34,.5)`, `dasharray 2.5 3`,
  width 0.55, `stroke-dashoffset: -24` over 5s linear infinite.
- **Stage** (`.hero-three`): three stacked gradients — a 145° navy base
  `#0c3b60 → #071b2f` at 78%, a blue lift `rgba(35,107,164,.52)` at 18%/22%, and
  a gold bloom `rgba(242,170,34,.16)` at 50%/52%.

I also rendered the reference standalone — extracted screen 3's markup plus the
page's stylesheet into a rig and screenshotted it headlessly at exactly 390×844 —
then **sampled it pixel-for-pixel against the Android build** rather than
eyeballing. That is what caught the three deltas fixed below.

## What shipped

**The stage is now one backdrop behind the wordmark *and* the pager.** The
mockup's gradient runs unbroken from the status bar to the white sheet, so it
cannot be painted per-strip the way the flat navy was. Pages now paint their own
background only when it differs from the backdrop (screen 2's cream); the navy
pages stay transparent, so the glow cross-fades under them as you swipe instead
of popping at the page boundary.

**The hero**: connector canvas → portrait card → six cards, in that z-order, so
the lines vanish under the cards at both ends exactly as the reference's
stacking does.

- **Dashes** use the reference's own geometry as fractions of the box width, so
  they hold at any size. The reference marches 24 units every 5s, which is 4.36
  dash cycles — a non-integer loop with a visible jump at restart. Animating one
  whole cycle at the same speed gives an identical rate and no jump.
- **Portrait**: gold bloom over the upper half, foot scrim, verified badge (navy
  on gold, per colour-system R1), role caption.
- The reference draws a **pulsing dot at each endpoint**; in its own stacking
  order they sit *under* the opaque cards and never show. Not reproduced —
  they would be dead pixels.

**Reduce-motion.** Added `rememberReduceMotion()` to the design package (Android;
iOS uses `accessibilityReduceMotion`) and gated the dashes on it — the reference
gates the same keyframes on `prefers-reduced-motion`. This also gives the Lottie
follow-up from 2026-08-15 a helper to use.

## Three deltas the pixel sampling caught

1. **Card heights.** The reference's `min-height` lets each card size itself,
   which leaves the two-line card ("trained for tense moments") taller than its
   neighbours and breaks the grid. All six are now pinned to the same height.
2. **Portrait bloom** was heavier than the reference's — reduced.
3. **The blue lift is a palette shortfall.** Sampled at the same proportional
   point, the reference reads `(22,77,121)` and ours `(21,45,72)`. Its
   `rgba(35,107,164,.52)` is a saturated mid-blue **the palette has nothing near**
   — Steel Blue is the closest and lands cooler and greyer at any alpha that does
   not wash the navy out. Deliberate shortfall, **for Blue Sky to rule on**, same
   class of issue as the gold-on-white eyebrow. Everything else matches.

## A real bug the narrow-width check found

Screen 3 was correct at 411dp. At **360dp** it broke: fixed card heights clipped
every label, and the portrait caption wrapped and overflowed the card.

The cause was sizing text in `sp` inside a box sized in percentages. The fix
follows the reference's own model — it sizes this graphic off the viewport
(`clamp(min, vw, max)`), not off the reader's font setting, so a
`ConstellationType` now derives every size from the width of the graphic and
converts through `Dp.toSp()` (which divides out the font scale). Card height is
the greater of the reference's 18% and what the copy actually needs.

**This makes the constellation's text ignore the OS font scale, deliberately.**
It is defensible only because the whole graphic is a single accessibility element
carrying a spoken description of all six credentials — a screen-reader user gets
every word regardless — and because the sheet copy below, which is the actual
reading content, still scales normally. Flagging it as a decision, not a detail.

## Verifying the animation (it took three tries to measure honestly)

Frame-diffing said the dashes were frozen. Two of my own probes were the cause:
an alpha probe had made the lines nearly invisible so the deltas fell under
threshold, and my hand-picked sample line was tracing the *card borders*, not the
connectors. Logging the value showed it animating correctly all along
(−4.4 → −5.4 → wraps to −0.35). Measured properly on a clean build:

- **Animations on:** ~700 changed pixels per frame pair, confined to the
  connector corridor — the dashes march.
- **`animator_duration_scale = 0`:** 0 changed pixels — reduce-motion works.

Worth recording: I twice drew a wrong conclusion from a diff before checking what
the diff was actually sampling.

## Files

- **kotlin**: `WelcomeScreen.kt` (shared stage backdrop, `drawStage`, Credentials
  routing), `WelcomeHeroes.kt` (`CredentialsHero`, `ConnectorNet`, `PortraitCard`,
  `CredentialNode`, `ConstellationType`), `AsiTheme.kt` (`rememberReduceMotion`),
  `res/drawable-nodpi/welcome_hero_lfr_portrait.jpg`.
- **swift**: `WelcomeScreen.swift` (`StageBackdrop`, Credentials routing),
  `WelcomeHeroes.swift` (same five types), `Media.xcassets/
  welcome_hero_lfr_portrait.imageset`.

No palette values were added — the stage and cards are built from Mid Navy,
Shield Navy, Steel Blue and Active Gold at alpha.

## API

None — pure UI.

## Tests

| Suite | Result |
|---|---|
| Android unit | **429 / 429**, 0 failed |
| Android instrumented (incl. AccessibilityTest, DynamicTypeTest) | **30 / 30**, 0 failed |
| iOS unit | **411 / 411**, 0 failed |

Visually verified on the **Pixel 8a emulator (411dp)**, at a forced **360dp**
narrow width, on the **iPhone 16 Pro** simulator, and on the **iPhone 12 mini**
(360pt) — screen 3 holds at every one.

The real Infinix was left alone: it was locked with an incoming call, and it is
the same 1080×2400 @420dpi as the emulator, so it would add nothing.

## Open issues / next steps

- **The blue lift needs a Blue Sky ruling** (above). It is the only visible gap
  against the mockup.
- **Screens 4, 5, 6 still await their mockups.** Screens 1–3 are now rebuilt.
- **Pre-existing, found in passing at 360dp / on the 12 mini:** screen 2's
  incident tiles clip their labels ("Questione d", "Pedestria n", "Traffic
  accident"), and the sheet body copy clips mid-glyph on short screens — it is
  scrollable so the text is reachable, but it looks broken. Neither is caused by
  this change; both are worth a pass.
- **The emulator died twice more** during this task, once mid-install. Disk is at
  11 GiB free of 460 GiB.
- The **`animator_duration_scale` was unset** on the fresh emulator; setting it
  explicitly to 1.0 is worth doing before any animation verification.
