# 2026-08-26 — Situations picker: the CodePen 27B sheet + glassy gold tiles

## Task

The Home "customize your situations" path opened a full-screen page (gold "THREE
CHOSEN" guidance card, footer hint, big square tiles). The user showed the
CodePen 27B design — a bottom sheet over the dimmed home — and asked to match it.
Repos: `kotlin`, `swift`.

## What the CodePen actually specifies (from the pen's own CSS)

Pulled `.gtile` / `.gtile.sel` from the full render of the pen:

- `.gtile` — glassy fill `linear-gradient(165deg, rgba(255,255,255,.14),
  rgba(255,255,255,.045))`, `1px solid rgba(232,160,32,.55)` gold border, faint
  gold glow, icon `#E8A020` (gold, 23px), label 10px/800 white.
- `.gtile.sel` — gold-tinted fill `rgba(232,160,32,.25→.07)`, brighter border
  `.95`, stronger gold glow, `transform: translateY(1px)`, and the icon flips to
  **`#3BA8FF` (neon blue)**; gold check badge (`.tick`, `#E8A020` bg, dark glyph).
- Sheet 27B: title "Your most common situations", subtitle "Choose up to three.
  They stay one tap from home.", 2-col grid, single **Done**, over a dimmed home.

## Decisions

- **Presentation → bottom sheet** (user chose this over a page restyle). Home
  already hosts `ModalBottomSheet`s for the connect tray (27A) and confirm (28),
  so 27B as a sheet is idiomatic and low-risk. Opened from Home's edit action;
  the full-screen `SituationsScreen` stays for the onboarding checklist (13C).
- **Selected icon stays palette gold, not the pen's `#3BA8FF`.** That neon blue
  is outside the Attorney Shield palette (Rank 1 is binding) and sits next to the
  explicitly "avoid" bright teal `#00B4D8`; the only sanctioned blue (Steel Blue
  `#8DA8C4`) is a *muted* colour that would make selected tiles read duller than
  unselected. So selection is carried by the gold-tinted fill + brighter border +
  gold check + glow — faithful to the pen's structure, legal on colour. Same
  honest-palette call as Call's REC badge and the timeline markers.
- **Save refreshes Home in place.** Home shows the chosen three
  (`chosenSituations`, derived from `readiness.situationIds`), so on save the
  sheet calls `refreshReadiness()` and closes — no navigation round trip. Done
  with no changes just dismisses.

## Files

- **kotlin** — `feature/situations/SituationsScreen.kt` (tile rebuilt to `.gtile`,
  now `internal` for reuse), `feature/situations/SituationsSheet.kt` (new,
  `ModalBottomSheet`), `MainActivity.kt` (Home hosts the sheet + a
  `SituationsViewModel`; `onEditSituations` opens it; save → `refreshReadiness`).
- **swift** — `Feature/Situations/SituationsScreen.swift` (tile rebuilt, now
  reusable), `Feature/Situations/SituationsSheet.swift` (new; picked up by the
  synchronized project folder), `AttorneyShieldApp.swift` (`.sheet` on Home with
  a drag indicator + `.large` detent; save → `refreshReadiness`).

## API endpoints used

None new. The picker's `SituationsViewModel` uses the existing situations
load/save; Home reads `situationIds` via profile readiness.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` | **BUILD SUCCESSFUL** |
| Android — `testDebugUnitTest` | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

## Next / notes

- The onboarding full-page (13C) keeps its guidance card, "Skip for now", and
  info-chip — appropriate for the setup step; it inherits the new tile look.
- Worth an on-device eyeball of the glow (`shadow` spot colour on Android vs
  `.shadow` on iOS render slightly differently) and label wrapping on the
  longest names ("Auto Accident", "Pedestrian Stop") in the compact tile.
