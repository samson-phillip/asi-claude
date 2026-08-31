# 2026-08-31 — Home pill reads "Free trial" for a trial member

## Task

A trial member saw **"Active · 24/7 coverage"** on Home yet was (correctly) gated
from the live attorney — confusing. Make the pill read as a trial instead.

## Change

Added a `Trial` state to the Home coverage pill, checked **before** the Active
branch (a trial is `entitled`, so `canCall` is true and it would otherwise fall
into Active). Order is now: grace → guest → **trial** → active.

- Label: **"Free trial"** (parallels "Guest explorer"); gold fill (`ctaBg`) to
  distinguish it from the green Active pill. Colour is a fill, never the text
  (colour-system R4), like the other pills.

Note: this is a deliberate divergence from member-client, which shows
"Active 24/7 Coverage." for a trial too (`HomeScreen.tsx:296`) — the user asked
for the clearer wording after hitting the confusion. The gate itself is unchanged
and still matches member-client.

## Files

- `swift/AttorneyShield/Feature/Home/HomeScreen.swift` — `HomePill.trial` + branch.
- `kotlin/app/.../feature/home/HomeScreen.kt` — `HomePill.Trial` + branch.

## Verification

Both compile. Could **not** screenshot the logged-in pill — the sim's session had
ended (it was at the login screen), and signing in needs credentials we don't use
on the sim. The change is a pure ordering + label edit gated on `model.isTrial`
(already unit-tested via `AccountGateTests`/`HomeViewModelTest`), so the risk is
low; eyeball it on a logged-in trial account to confirm "Free trial" shows.

## Related

The underlying "why is a converted trial still a trial" is a backend issue —
written up for Innocent in `notes/backend-trial-conversion-not-settling-for-innocent.md`.
