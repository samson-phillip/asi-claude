# 2026-08-31 — Welcome screen: complete the shield logo + flatten the sheet top

## Task

Two mismatches between the Welcome carousel and the CodePen (member-reported,
with side-by-side screenshots):

1. **Logo cut off.** The shield in the "Attorney Shield" title showed as a
   clipped "tent" shape instead of the CodePen's complete two-tone shield.
2. **Bottom sheet corner radius.** The white bottom half had rounded top corners;
   the CodePen has a straight horizontal edge where the dark stage meets it.

Everything else on those screens already matched.

## Root cause

The logo bug was a **malformed asset**, not a layout bug. `brand_shield.png`
(shipped in both repos) is corrupted: the shield is clipped and streaked over
mostly-empty space, so at any size it renders as a cut-off mark. The correct,
complete mark already existed as a resolution-independent vector — Kotlin's
`ic_brand_shield.xml` and Swift's `brand_shield_hero.svg` (both viewBox 100×114,
the same two-tone heraldic shield the Home hero uses).

## Fixes

**Logo — point the lockup at the good vector (dropped the broken PNG):**
- kotlin: `AsiComponents.ShieldLockup` → `R.drawable.ic_brand_shield` (was
  `brand_shield`). Home already used the vector, so Kotlin Home was fine.
- swift: `AsiComponents.ShieldLockup` → `Image("brand_shield_hero")` (was
  `brand_shield`). **Also fixed `HomeScreen.HomeBrand`**, which used the same
  broken PNG — so Swift's Home logo was cut off too. Both now use the vector.
  (`brand_shield_hero` has `preserves-vector-representation`, so it stays crisp at
  the 20–21pt lockup size.)

**Bottom sheet — straight top edge:**
- kotlin: `WelcomeScreen` white `Surface` shape `RoundedCornerShape(top 28dp)` →
  `RectangleShape` (kept the `shadowElevation`).
- swift: `WelcomeScreen` white background dropped
  `.clipShape(.rect(topLeadingRadius: 28, topTrailingRadius: 28))`.

Stale doc comments referencing `brand_shield.png` / "no brand asset yet" were
corrected on both sides. The malformed PNGs are now unreferenced; left in place
(harmless) rather than deleted.

## Decision — scope

The user pointed at the Welcome screen, but the logo defect came from a shared
asset. On Kotlin only Welcome was affected (Home already used the vector); on
Swift the same broken PNG was also on Home, so I fixed both usages rather than
knowingly leave an identical cut-off logo on Home. Same one-line swap, same
defect.

## Test results

- **Android**: `:app:compileDebugKotlin` — BUILD SUCCESSFUL.
- **iOS**: `xcodebuild build test` (WelcomeContentTests) — BUILD + TEST SUCCEEDED.

Changes are visual; a live screenshot is still pending (emulator session
expired). Root cause was confirmed directly by viewing the malformed PNG and the
correct vector, so confidence is high.
