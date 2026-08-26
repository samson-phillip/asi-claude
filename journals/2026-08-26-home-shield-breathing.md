# 2026-08-26 — Home shield hero: match the CodePen's breathing rings

## Task

The Home guardian shield's rings breathe in the CodePen; the user asked me to
check the pen for that effect. Repos: `kotlin`, `swift`.

## What the CodePen actually does

The reference-doc transcription (`notes/design-reference-codepen.md`) only lists
the tour spotlight pulse in its Motion section — it missed the resting Home
hero. So I pulled the pen's own source (full render of
`https://codepen.io/leejesse70/full/YPNOGaM`) and read the CSS.

Markup (screen 27 guardian hero):

```html
<div class="gstage">
  <div class="gaura"></div>     <!-- soft gold radial halo -->
  <div class="gring a"></div>   <!-- outer ring -->
  <div class="gring b"></div>   <!-- inner ring -->
  <div class="gshield">…svg…</div>
</div>
```

CSS (verbatim):

- `.gaura` — 170px gold radial gradient, `animation: gaura 2.4s ease-in-out
  infinite alternate`; keyframe `scale .88→1.1, opacity .55→1`.
- `.gring` — `border: 1.5px solid rgba(232,160,32,.32)`, `animation: gring 2.4s
  ease-in-out infinite alternate`; keyframe `scale .94→1.06, opacity .5→1`.
- `.gring.a` — 134px.
- `.gring.b` — 108px, `border-color: rgba(232,160,32,.48)` (brighter),
  **`animation-delay: -1.2s`** — half the pass, so the inner ring breathes in
  counterpoint to the outer.

The distinctive read is the two rings *counter-breathing* — one drawing in as
the other pushes out — not a single throb.

## The gap in our build

Both platforms already had an aura + two rings + a 2.4s breath, but:

| | CodePen | Ours (before) |
|---|---|---|
| Two rings | inner offset −1.2s → out of phase | shared one scale → in unison |
| Ring scale | .94→1.06 (±6%) | .97→1.0 (±3%, muted) |
| Opacity pulse | aura .55→1, rings .5→1 | none |
| Inner ring alpha | .48 (brighter) | .32 |
| Period (Swift only) | 2.4s each way (4.8s round trip) | 2.4s round trip (2× too fast) |

## Change

Tuned both platforms to the pen's own values:

- **Kotlin** — two phases off one `rememberInfiniteTransition`: `breathA` (aura +
  outer ring) and `breathB` (inner ring, `initialStartOffset =
  StartOffset(1200, FastForward)`). Aura + rings now animate scale *and* opacity
  via `graphicsLayer`. Easing switched `FastOutSlowInEasing → EaseInOut`
  (cubic-bezier .42,0,.58,1 = CSS ease-in-out).
- **Swift** — two clock-driven phases (`breathA`, `breathB` shifted +1.2s), pure
  functions of the `TimelineView` clock. Fixed the cosine period to a 4.8s round
  trip (`/ 2.4`); it had been `/ 1.2`, a 2.4s round trip — breathing twice as
  fast as the reference *and* out of step with Android.
- Reduced motion now rests both phases at 0.5 (cycle mid-point) so the shield
  still reads lit rather than dim.

Colour stays palette gold (`AsiPalette.activeGold`), per design authority Rank 1
— the pen's literal `rgba(232,160,32)` is its own gold, not ours.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

Animation-only change; no ViewModel or test surface touched.

## Note for the reference doc

`design-reference-codepen.md` Motion section (§ "Motion", ~line 1011) is missing
the Home hero breath. Worth adding `gaura`/`gring` there next time that doc is
revised, so the transcription matches the pen.
