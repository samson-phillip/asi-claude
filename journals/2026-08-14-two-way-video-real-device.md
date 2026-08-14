# 2026-08-14 — Two-way video, for real, on a real device

## What happened

A member on a **physical Android phone** (Infinix X6886, tethered) placed an
auto-match call. It routed to the attorney (Samson) on the **LFR desktop
portal**. He accepted, and **both sides saw live video** — member and attorney,
each other's feed, on real hardware.

That is the core promise of the product — live attorney by video during an
encounter — working end to end for the first time. Everything before today was
either routing proven at the API layer, or the attorney half alone (the member
was a `curl` with no camera). This is the whole loop, with two real video
clients.

## The bug that had been hiding it: the call screen was unreachable

Testing on a real device (no emulator ANR to mask it) exposed it immediately:
tapping the shield → a situation just returned to Home. No call screen, no
`member-call`, nothing. The logs showed the bottom sheet opening and closing and
the app staying on Home.

The cause, in `MainActivity`'s `AppRoot`:

```kotlin
val destination = remember(destinationName) {
    val restored = Destination.valueOf(destinationName)
    if (restored == Destination.Call) Destination.Home else restored   // <-- always
}
```

The remap exists for one real case: a call can't survive activity recreation, so
a **restored** "Call" (after process death) should land on Home. But
`remember(key)` recomputes on **every** `destinationName` change, so it also
rewrote an ordinary `navigate(Destination.Call)` straight back to Home. The Call
branch never rendered, `CallViewModel` never mounted, `member-call` never fired.

That is exactly "the call won't connect" — and it was silent, because the
member never left Home.

Introduced in `d0942a4` ("Harden navigation state, dynamic type, offline and
token expiry"). A hardening pass broke the core feature, and it went unnoticed
because every prior call test was either the emulator (ANR'd before this point)
or `curl` (bypassed the app UI entirely). **A real device was what finally
showed it.**

### The fix

Read `destination` directly, and move the "restored into a call → Home" guard to
a one-time `LaunchedEffect(Unit)` at first composition. A genuine in-session
navigate to Call now works; a process-death restore into Call still lands on
Home.

**iOS never had this** — it navigates with a plain `@State` (`destination = .call`
directly), no derived remap. Checked explicitly.

## The live sequence (real device + LFR portal)

1. Installed the fixed build on the Infinix, signed in as `munyira851`.
2. Shield → **Test Call**. This time it reached **"Connecting you to an
   attorney"** — logs: `libopentok.so` loaded, OpenTok 2.32.1,
   `VonageSession: session connected`, camera connecting.
3. The call rang Samson's **LFR desktop** (dev-v0.5.28, online, no queue).
4. Samson **accepted** → both feeds live: member video on the phone, attorney
   video in the portal. Confirmed by the user.

The one earlier snag — the ~30s ring window elapsing while I switched from the
phone to the desktop — the user resolved by accepting on the portal directly.

## Verified along the way

- Auto-match routing (no `queueId`, no `attorneyId`) → 200 → Samson, with the
  attorney online. 409 when none online (correct).
- The location factor held: the phone's real location resolved to a country
  Samson covers.
- OpenTok/Vonage runs fine on **real hardware** — the "connecting forever" was
  only ever the emulator/simulator's inability to run the video SDK.

## Test results

Android **424 / 0** (the nav fix changed no unit-tested surface; the proof is
the live device run). iOS **402 / 0**, unaffected.

## Open issues / next steps

- **A Compose UI test for navigation** would have caught this; the unit suite
  can't see `AppRoot`'s state derivation. Worth adding a test that asserts
  `navigate(Call)` actually renders the call destination.
- Nothing else outstanding on the call path.
