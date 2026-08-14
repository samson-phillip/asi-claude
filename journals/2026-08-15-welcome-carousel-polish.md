# 2026-08-15 — Welcome carousel UI polish: real graphics from the CodePen

## Task

"Polish the UI like in the CodePen — apply the graphics from the CodePen screens
to the mobile app." Scoped (with the user) to the **welcome carousel first**, and
to **recreate the graphics in Compose** — with the explicit note that many of the
reference graphics are SVGs, so port them as real vector assets rather than the
emoji/placeholder stand-ins the app shipped with.

The carousel already had code-drawn heroes ([WelcomeHeroes.kt](../kotlin/app/src/main/java/com/attorneyshield/member/feature/welcome/WelcomeHeroes.kt)),
but three were placeholders vs. the reference: screen 2 (dark, text-only tiles),
screen 4 (a text grid, not the card deck), and screen 6 (a lone ★, no US map).

## Getting the reference's actual SVGs (the cross-origin wall, solved)

The planning journal noted the CodePen renders inside a cross-origin `cdpn.io`
iframe, so JS can't read the pen's DOM from the `codepen.io` page. Workaround that
worked: **navigate the browser tab directly to the iframe's own URL**
(`https://codepen.io/leejesse70/fullpage/YPNOGaM`, which redirects to `cdpn.io`),
then reach through the one remaining nested same-origin iframe via
`iframe.contentDocument`. That exposed all **400** of the pen's SVGs, plus computed
styles, so every colour/hex/position below was read from the source, not guessed.

Key finding: the reference's icon graphics split into two kinds —
- **Clean hand-authored SVGs** (screen 4 tool icons: cloud/gps/lock/folder) — port
  verbatim.
- **Lottie animations rendered to SVG** (screen 2 incident icons — multi-layer,
  `__lottie_element` clip paths, matrix transforms). Not worth flattening or adding
  a Lottie runtime for; recreated as a cohesive static line set instead.
- Screen 6's "map" is a **142 KB bundled JPEG** (raster), not a vector at all.

## What shipped (screens 2, 4, 6)

**New asset pipeline.** The app had *zero* image assets (100% emoji + code-drawn).
Introduced `app/src/main/res/drawable/` with 11 VectorDrawables, all tinted at the
call site so they stay theme-aware (gold on dark / navy on light):

- **Screen 4 — tool icons + card deck.** `ic_tool_{cloud,gps,lock,folder}.xml`
  converted from the reference's own clean SVG path data. Rebuilt
  `ProtectionToolsHero` from a static text grid into the reference's **rotating
  card-deck with a progress-dot row**, each card carrying its real icon.
- **Screen 2 — cream hero + incident icons.** Read the reference's exact tile
  styling from the pen: solid gold tiles (`#F2AA22`) with **navy** (`#071B2F`) line
  icons + labels, on a **cream** phone background. Rebuilt `IncidentTilesHero` as a
  cream panel (`OffWhite`) with solid-gold tiles using `ctaBg`/`ctaFg` (the brand's
  own gold-with-navy pairing). Authored 5 static line icons
  (`ic_incident_{traffic_stop,questioned,domestic,car,pedestrian}.xml`) in one
  visual language, since the source icons are Lottie.
- **Screen 6 — US map + activity lights.** The reference bundles a raster map JPEG.
  Per the user's choice ("code-drawn US map + lights"), sourced a **public-domain
  (CC0, OpenClipart via freesvg.org) single-path US silhouette** → `ic_us_map.xml`
  (viewBox 675×419, ~6 KB), tinted muted-grey, with **5 pulsing gold activity
  lights** placed at the reference's own fractional positions (read from its
  `.map-activity-light` px coords over the 276×178 map card). `rememberInfinite
  Transition` ping rings, gated by an `animate` flag for reduce-motion/tests.

Screens 1, 3, 5 were left as-is (already presentable; screen 1's "video" is a photo
in the reference, which we can't reproduce natively). Deferred per the user.

## Files

- **Modified:** `feature/welcome/WelcomeHeroes.kt` (screens 2/4/6 heroes,
  `ActivityLight`, `DeckCardBack`; new imports for `Image`/`ColorFilter`/
  `painterResource`/`BoxWithConstraints`/infinite-animation).
- **New (11):** `res/drawable/ic_tool_{cloud,gps,lock,folder}.xml`,
  `ic_incident_{traffic_stop,questioned,domestic,car,pedestrian}.xml`,
  `ic_us_map.xml`.
- No copy/data changes (`WelcomeContent.kt` untouched).

## API

None — pure UI.

## Verification (on the Infinix X6886, Android 15)

Installed and screenshotted each reworked screen:
- **Screen 4:** card deck rotates cloud → gps → lock → folder, each with its real
  line icon; 4-dot progress row, active dot widened + gold. All four icons render
  correctly (incl. the rect/circle→path conversions for lock/gps).
- **Screen 2:** cream hero, green "Live" pill, five gold tiles with legible navy
  icons.
- **Screen 6:** recognizable continental-US silhouette with gold lights pulsing at
  the western, central, south-east cluster, and north-east positions.

`./gradlew connectedDebugAndroidTest` — **30 / 30 passed, 0 failed.** No regression,
and the infinite map-light animation does not hang the welcome tests (page 6 is not
composed while the carousel sits on page 1).

## Open issues / next steps

- **Screens 1 & 3 finishing touches** (secure/verified icons on the live-call hero;
  per-stat icons on the credential grid) — deferred as lower priority.
- **Home screen** is the next high-impact target: the "gold shield hero" is
  currently the emoji `🛡`, incident tiles use emoji glyphs, and the bell/tab bar
  are emoji — all candidates for the same vector-asset treatment.
- The reference's incident icons are animated Lottie; if animated tile icons are
  ever wanted, that's a Lottie-Compose dependency + the source `.json`, not these
  static vectors.
