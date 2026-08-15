# 2026-08-15 — Welcome carousel rebuilt to the client mockups (screens 1 & 2)

## Task

The client sent fresh mockups for the welcome carousel. Rebuild it to match,
both apps, taking assets and colours from the CodePen reference. Screens 1 and 2
delivered here; 3–6 pending their mockups.

## The two decisions the user made

Asked up front because they cut against the binding rules:

1. **Hero photo** → *pull the CodePen asset.* The reference embeds the attorney
   photo as a base64 `data:` JPEG on `.live-counsel-frame > img`. Extracted it
   (547×820, ~47KB) and bundled it: Android `res/drawable-nodpi/`, iOS
   `Media.xcassets`.
2. **Red LIVE badge** → *use the red.* The mockup's badge is red, which the
   colour system forbids. The user signed off on matching it, so `#E34242` (the
   CodePen's own `.live-pill` colour) is added as **the one documented exception**
   to the closed palette — kept out of `AsiPalette.all` so the eleven brand
   values stay closed, and used only for the live/on-air badge.

## The chrome: a per-page stage over a fixed white sheet

The mockups revealed the real structure — the top **stage is per-page**, not a
fixed navy:

- **Screen 1**: dark navy stage, the video-call card floating with a navy margin.
- **Screen 2**: full-bleed **cream** stage, the incident content edge to edge.
- The **wordmark and status-bar icons flip** to suit the stage (white on navy,
  navy on cream).
- The **white content sheet** below — eyebrow, headline, body, dots, Register /
  Log in — never changes.

It is deliberately **fixed two-tone**, independent of the OS light/dark setting:
onboarding is a branded moment. Each zone pins its own appearance (Android nests
`AsiTheme(darkTheme=…)`; iOS overrides `\.asiColors` and `preferredColorScheme`).

### Screen 1 hero
Photo cropped to the face (`object-position 50% 26%`), a top+bottom scrim for
legibility, then the reference's affordances: red LIVE badge, SECURE badge (gold
shield), the "You" self-view tile, the verified-attorney caption with a gold
shield badge, and the mic / video / flip control bar. The controls are
**illustrative, not interactive** (this is marketing, not the call screen), so
the whole card is one accessibility element and nothing unlabeled is tappable.

### Screen 2 hero
Navy "Attorney network ready" banner with a gold shield chip and a gold LIVE
pill, then a 2×3 grid of gold tiles — each a white icon chip (navy icon) plus a
navy label — for the five incidents plus the reference's scope line as a
catch-all sixth tile.

## One deviation from the mockup, on purpose

The eyebrow ("24/7 LIVE COUNSEL", "ALWAYS READY") is **navy, not the mockup's
gold**. Gold on white is 2.85:1 and fails WCAG at any size (colour-system R3);
`accentText` is navy on light for exactly this reason. Flagged to the user; the
red badge was a deliberate exception, the gold-on-white eyebrow is a worse
failure and stayed in-palette.

## Files

- **kotlin**: `WelcomeScreen.kt` (per-page stage chrome), `WelcomeHeroes.kt`
  (photo hero + full-bleed incident tiles), `WelcomeContent.kt` (sixth tile),
  `AsiColors.kt` (`LiveRed`), 5 glyph vectors (`ic_wc_*`), the bundled photo,
  `PaletteAllowlistTest.kt` (allow `E34242`).
- **swift**: same shape — `WelcomeScreen.swift`, `WelcomeHeroes.swift`,
  `WelcomeContent.swift`, `AsiColors.swift` (`liveRed`), `Media.xcassets`. iOS
  uses SF Symbols for the glyphs (no palette-test change needed — `liveRed`
  isn't in `all`).

## Tests & live verification

- **Android 429 / 0** unit; **DynamicTypeTest + AccessibilityTest** green on the
  emulator (copy still reachable at 2× font; every tappable still announces).
- **iOS 410 / 0** unit.
- **Visually verified on the emulator (Android) and simulator (iOS)** — screens
  1 and 2 match the mockups on both platforms. iOS screen 1 needed one fix: a
  `scaledToFill` image handed an infinite-height frame blew the card up (badges
  and control bar clipped); moving the photo to a clipped `.background` and
  capping the card height fixed it.

## Real shield logo + animated icons — done (both apps)

The user pointed to `code_pen_design.html` for the actual assets. Two additions:

**The brand shield mark.** The reference's wordmark shield (identical paths in
the `brand-mark` and `intro-shield` SVGs) is a two-tone gold shield with a
cream/white monogram. No CLI rasteriser was available, so I rendered the SVG to
a transparent PNG **in the browser** (canvas `toDataURL`, data: URIs are
canvas-safe), then bundled it — Android `res/drawable-nodpi/brand_shield.png`,
iOS `Media.xcassets/brand_shield`. It replaces the drawn `ShieldLockup`
placeholder on both platforms and carries its own colours, so it reads on both
the navy and cream stages.

- *Snag:* the canvas PNG crashed Android's `painterResource`
  (`null cannot be cast to BitmapDrawable`) — the raw canvas encoding wasn't
  something aapt/BitmapFactory accepted. Re-encoding it through `sips` to a clean
  baseline PNG fixed it. (The JPEG hero was unaffected.)

**The animated incident icons.** Screen 2's icons in the reference are **Lottie
animations**, built programmatically by a JS builder (`AttorneyShieldLotties`).
I ran that builder in **Node** to emit the five Lottie JSONs (trafficStop,
questioned, domestic, trafficAccident, pedestrian — 4–9KB each, two-tone
navy/gold, 64×64@30fps) and bundled them: Android `res/raw/incident_*`, iOS
`Resources/Lotties/`. They now play looping in the tiles:

- Android: added `lottie-compose`; `LottieAnimation(RawRes, IterateForever)`.
- iOS: added `lottie-ios` via SPM (hand-edited the pbxproj to mirror the Vonage
  package wiring — new stable IDs `…201/202/203`; resolves Lottie 4.6.1);
  `LottieView(.named).looping()`.

The sixth "All law enforcement-initiated encounters" tile has no Lottie in the
reference and keeps the static shield.

### Tests & verification (both additions)
- **Android 429 / 0**; Accessibility + DynamicType green on the emulator.
- **iOS 411 / 0**.
- **Screens 1 & 2 re-verified** on emulator + simulator: shield mark in the
  wordmark, and the animated two-tone icons in the tiles, on both platforms.

## Branch note

`kotlin` is on **`dev`** (a gitflow — main/dev/uat/prod — set up in parallel;
the welcome work sits on top of a parallel "real graphics" commit, `4927f7e`,
which it preserved). `swift` and `asi-claude` are on **`main`**. Recommendation
given to the user: keep kotlin on dev, leave the others on main unless they want
swift brought onto the same flow.

## Open / next

- **Screens 3–6** await their mockups; they currently render as navy-stage cards.
- **Reduce-motion**: the Lottie icons loop unconditionally; gating them on the OS
  reduce-motion setting (as the CodePen does) is a small follow-up.
- The **intro splash** (`intro-shine` shimmer) is not built — frame 0 isn't a
  carousel page here.
