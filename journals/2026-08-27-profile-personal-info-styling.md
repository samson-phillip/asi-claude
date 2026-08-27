# 2026-08-27 — "Profile & personal info" brought up to the Account design

## Task

The Account → "Profile & personal info" detail screen looked undesigned — a
descriptor line plus flat Name/Email pairs on the bare background, unlike the
card-based sibling panes. Requested to match the design.

## Finding

There is **no dedicated CodePen spec** for this detail screen — the design notes
(screen 33) only list "Profile & personal info" as a *row* in the Account
overview, and 33A–33C are the other sub-screens; onboarding "Personal details"
(screen 10) is a different, setup-flow screen. Confirmed with the user, who chose:
**style it to the app's own Account design** (rather than dig up a CodePen for it).

## Change (both platforms)

Wrapped the Name/Email into the app's Account-detail card treatment — a
`surface` card with a `border` hairline and a divider between the two rows, each
row padded like the nav-row groups — matching the membership card and the
grouped nav rows on the same screen. No new fields or editing (only the name +
email the session already holds).

- `kotlin` — `feature/account/AccountScreen.kt` (`ProfilePane`, `ProfileField`).
- `swift` — `Feature/Account/AccountScreen.swift` (`profilePane`, `profileField`).

## Verification

- Android: **verified live on the emulator** (John Doe / salmson93@gmail.com) —
  Name/Email now render inside a bordered card with a hairline divider.
- iOS: `xcodebuild` + `ScreenRenderTests` **TEST SUCCEEDED**.

## Note

If a CodePen for this screen turns up later with more (avatar, phone, DOB,
address, or edit controls), it's an easy follow-up — this was scoped to the
name + email the app has today.
