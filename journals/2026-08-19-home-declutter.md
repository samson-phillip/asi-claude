# 2026-08-19 — Home to the CodePen: remove the non-design extras

## Task

Bring Home closer to the CodePen by removing elements the design doesn't have.
Home is the landing screen, so this is the highest-visibility parity win.
Repos: `kotlin`, `swift`.

## Removed (not in the reference's Home)

1. **The "Connect with" attorney-picker chips** (Auto-match + per-attorney).
   Routing is jurisdiction-wide auto-match, chosen in the connect flow, not on
   Home. Removed the chip row + the now-unused `AttorneyChip` component on both
   platforms. The view-model plumbing (`attorneys`, `selectedAttorneyId`,
   `selectAttorney`) is left intact — it's harmless and the connect flow may use
   it — just not surfaced on Home.
2. **The secondary "Open your Glovebox" button.** The 4-tab bar reaches the
   Glovebox (and Profile → My documents does too), so the extra button was
   redundant. Confirmed the tab bar exists on **both** platforms before removing
   (the old iOS comment "the other three tabs do not exist yet" was stale).
3. **The routing-hint line** under the tiles.

## Kept deliberately

The situations section stays as the app does it — **2-column cards, and the full
incident grid for the empty state** rather than the reference's three dashed
placeholders. That was the one divergence the user chose to keep. Its conditional
heading ("Your most common situations" when chosen / "What's happening?" over the
full grid) follows from that kept layout — a full list of every option isn't
honestly "your" situations — so it stays too. The grace/expired Home state (screen
35) is still unbuilt; it only shows for a lapsed account, off the demo path.

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` (no unused-import warnings) | **BUILD SUCCESSFUL** |
| iOS — build | **BUILD SUCCEEDED** |

## Next

Account (Family dashed spot-cards, Settings pane, hub email), then Activity
outcome labels (per backend A1), then Notifications split.