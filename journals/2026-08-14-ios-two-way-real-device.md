# 2026-08-14 — iOS two-way video, on a real iPhone

## Result

A member on a **physical iPhone** (Christian's iPhone 14 Pro Max) placed a call
that routed to the attorney (Samson) on the **LFR desktop portal**, was accepted,
and **both video feeds went live** — confirmed by the user watching both ends.

That closes the parity gap: two-way attorney video is now proven on real
hardware on **both** platforms — Android (Infinix X6886) earlier today, iOS now.

## How the real iPhone was driven

I can't tap a physical iPhone with the screenshot tools (those are simulator
only). The way to drive a real device's UI is an **XCUITest**, so I wrote a
throwaway one (`LiveCallUITest`) that:

1. Signs in as the dev member (defensive: skips if already signed in).
2. Skips the tour, dismisses any nudge.
3. Taps the hero shield → **Test Call** (tray tile by accessibility label).
4. Grants the camera/mic prompt via SpringBoard (`Allow`).
5. Waits for the **"Connecting you to an attorney"** screen — proof the
   member-call fired and the Vonage session came up on the device.
6. Holds ~2 min so the attorney can accept.

Run on the device with:
```
xcodebuild test -destination 'platform=iOS,id=<iPhone udid>' \
  -only-testing:AttorneyShieldUITests/LiveCallUITest \
  -allowProvisioningUpdates DEVELOPMENT_TEAM=TWKX78WDP7
```

**The harness was removed, not committed** — it signs in with dev creds, sleeps
two minutes, and needs a real device + live backend, so it is a manual tool, not
a CI-safe test (same call I made with the temporary org-debug log). This journal
is the record of how to recreate it.

## Two signing gotchas (for next time)

1. **`platform:iOS,id=` wants the hardware UDID** (`00008120-…`), not the
   `devicectl` core-device UUID. Get it from `xcrun xctrace list devices`.
2. **The test targets had no development team** — only the app target set
   `DEVELOPMENT_TEAM`. Device UITests sign the test runner too, so pass
   `DEVELOPMENT_TEAM=TWKX78WDP7` on the `xcodebuild` line (automatic signing did
   the rest — the device is registered in that team).

The iPhone 12 Pro Max ("iPhone") wasn't usable: *"developer disk image could not
be mounted"* — Developer Mode/trust not set up. Christian's iPhone 14 Pro Max was
ready and is the device this ran on.

## What this confirms

- The iOS app builds, signs (production team `TWKX78WDP7`), installs, launches,
  and runs the whole call flow on a real device.
- OpenTok/Vonage publishes and subscribes fine on real iOS hardware — the
  "connecting forever" seen before was only ever the simulator's missing camera.
- The console showed **"Connected"** with the member's stream (not "Waiting for
  member…"), i.e. the iPhone was genuinely publishing.

## Disk note

The Mac hit ~99% full twice during the device builds (the "codesign internal
error" is a disk-full symptom). Cleared regenerable caches — `ModuleCache`, the
Android `app/build`, the other project's DerivedData, the simulator products, and
scratchpad screenshots — to keep the device builds signing. Worth watching; the
DerivedData for device + simulator builds is large.

## Open issues / next steps

- Nothing outstanding on the call path — both platforms proven end to end on
  real devices.
- Still open from the backend write-up: **item 4 (current location)** —
  `currentCountry`/`currentSubdivision` for travel routing (optional).
