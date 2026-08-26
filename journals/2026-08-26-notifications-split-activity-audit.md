# 2026-08-26 — Notifications split (24/26) + Activity parity audit

## Task

Close out the last two screens on the CodePen parity punch-list: **Activity**
(screen 32) and **Notifications** (screens 24 + 26). Repos: `kotlin`, `swift`.

## Activity — already at parity (audit + doc fix)

Reviewed both platforms against CodePen screen 32. The screen was already built
correctly in an earlier session:

- Vertical timeline with the join event as its origin ✓
- Type · date · duration · attorney per row ✓ (attorney from the flat
  `attorneyDisplayName` field, never the nested resolver that hangs the gateway)
- No REC badges / no replay links ✓
- Outcome markers + labels ("No attorney answered", "You ended the call") — a
  step beyond the reference, and honest about what happened
- **View transcript dropped** — the one honest divergence, per backend A1 (no
  transcript API is scheduled; a dead link would be worse than none)

The only defect was a **misleading doc comment** on both platforms: it claimed
attorney names were absent (they are shown) and cited stale ask codes (A8/B6)
instead of the current A1 decision. Corrected the comment on both; no behaviour
change.

## Notifications — split screen 24 from screen 26

The bell opened a single screen that was the notification **centre** (24) with
the full **preferences** pane (26) scrolled below it. Account → Settings → Push
notifications opened the *same* merged screen.

The CodePen draws these as two distinct screens:
- **24 — Notification centre** (bell): Finish-setup items with one-tap actions,
  then a read-only "Earlier" feed with a "Mark all read" control.
- **26 — Notification settings** (Settings → Push notifications): four category
  toggles (safety-critical locked on), a frequency dial, plus the separate
  marketing-consent switch.

The merge was documented as necessary because "the design's own navigation has
no route to a standalone notification-settings screen" — but that premise was
false: the `onOpenNotificationSettings` route from Account Settings already
existed and pointed at the merged screen. The merge dated from when screen 26
was two switches; B8 grew it to six controls plus a dial, so a calm centre and a
separate settings screen is now both faithful and better UX.

### Change

- New screen **`NotificationSettingsScreen`** (26): lockup + Close, "Notifications"
  title, "Choose what you hear about…" standfirst, then the toggles + dial body.
- **`NotificationsScreen`** (24) drops the settings section; the bell still lands
  here and Close returns Home.
- New destination — `Destination.NotificationSettings` (Kotlin) /
  `.notificationSettings` (Swift). Account Settings → Push notifications routes
  to it; Close returns to Account (the pane the member came from). The bell keeps
  routing to the centre.
- The shared `NotificationsViewModel` is unchanged — both screens read the same
  state and prefs, so the VM unit tests are untouched.

## API endpoints used

None new. Both screens read the existing notifications state / preferences
(`setPreferences`, `markRead`, `markAllRead`).

## Verification

| Suite | Result |
|---|---|
| Android — `compileDebugKotlin` | **BUILD SUCCESSFUL** (one pre-existing `LocalLifecycleOwner` deprecation, unrelated) |
| Android — `testDebugUnitTest` | **BUILD SUCCESSFUL** |
| iOS — build (iPhone 16 Pro sim) | **BUILD SUCCEEDED** |

## Status — CodePen parity punch-list

With Activity confirmed and Notifications split, the ranked parity punch-list is
**clear**. Remaining items are all previously-flagged, backend- or art-blocked,
not parity gaps:

- Account hub-row reorg (needs "PIN & security" / "Support & intro video" screens)
- Settings "Language" row (needs a locale switcher)
- Glovebox field masking (backend A3 sensitive-field flag) + per-section watermarks (art)
- `null`-vs-`[]` transport-layer normalisation
- Country-specific empty states

## Demo caveat

Sign in as a US or KE member (e.g. `claire-member@…` on dev) or the Glovebox and
incident tiles look empty.
