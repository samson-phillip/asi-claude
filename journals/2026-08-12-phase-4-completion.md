# 2026-08-12 — Phase 4 completion

## Task
Finish the remaining hardening: screen-reader pass, airplane mode, performance,
and the iOS dynamic-type gate flagged as owed.

## What was done

### Screen-reader pass — as a gate, not a sweep

`AccessibilityTest` walks the semantics tree of Welcome, Login, Home, the live
call and the connecting state, and fails on **any clickable node that announces
nothing** — no content description, no text, no editable text.

Written as a walk rather than a checklist because a control added later without a
label then fails here instead of shipping. A TalkBack user who reaches an
unlabelled button hears "button" and nothing else, and on this app that could be
the button that reaches an attorney.

All five screens pass. The icon-only controls that mattered — the avatar, the
gold shield hero, the password Show/Hide toggle, and the page indicator — were
already labelled and are now pinned.

### Airplane mode — verified end to end on device

Airplane mode on, sign-in attempted, and the app showed:

> You appear to be offline. Check your connection and try again.

rather than a raw `Unable to resolve host`. Email and password survive, and the
button stays available to retry.

### Performance — and a real finding underneath it

Cold start on the debug build measured 1.4–4.6s across five runs, which is not a
meaningful number: a debug build is not minified, is debuggable, and runs on an
emulator. Chasing it would have been measuring the wrong thing.

Looking at the release configuration instead turned up something that mattered:

**`isMinifyEnabled = false`, and the `proguard-rules.pro` it referenced did not
exist.** So release had never been minified, and nothing had ever verified the
app survives R8 — a failure class that appears only in release builds, typically
as a reflection error inside a third-party SDK.

Fixed:
- Wrote the rules file, with keep rules for the Vonage SDK (JNI + reflective
  class lookup, and the library most likely to break), kotlinx.serialization's
  generated serializers, and OkHttp's optional dependencies.
- Enabled `isMinifyEnabled` and `isShrinkResources`.
- Signed release with the debug key **temporarily**, so a minified build can
  actually be installed and smoke-tested. Needs a real keystore before shipping.
- Set `versionCode = 127`, since the shipping app was found at 126 and anything
  lower is treated as a downgrade. **Confirm against the real store value** — 126
  is only what one dev device happened to have.

Result: R8 completes, the APK drops **49.5 MB → 39.1 MB**, and the minified build
installs, launches and navigates with no `SerializationException`,
`ClassNotFoundException`, `NoSuchMethodError` or `UnsatisfiedLinkError`.

**Still unverified under R8:** response decoding and the Vonage call path, both of
which need a login the gateway URL still blocks. Same wall as everywhere else.

### iOS dynamic-type gate — asymmetry closed

Added an `AttorneyShieldUITests` target. This has to be a UI test: the failure
being guarded against is visual (text clipped out of a fixed-height container),
and SwiftUI layout cannot be asserted from a unit test without a third-party
inspector.

Three tests, driven through the launch argument the OS itself honours so the app
needs no test-only code path. They assert the welcome headline appears at
`AccessibilityXXXL` and that Register and Log in are not merely present but
**hittable** — the earlier bug was text that existed and could not be reached.

## Test results

**Android — 129 unit + 20 instrumented, 0 failures.**
**iOS — 129 unit + 3 UI, 0 failures.**

## Problems hit

**The emulator became unstable and died twice mid-run**, once reporting "No
connected devices" and once refusing to start because my `pkill` had not fully
cleared the previous instance ("Running multiple emulators with the same AVD").
Killing `qemu-system` explicitly and waiting fixed it.

**The machine's disk is at 97% (13 GiB free)**, which is very likely contributing
to that instability. Flagged for discussion rather than acted on.

**`adb shell input text` races field focus.** An early attempt typed "mmem" into
the email field because the tap had not settled. Needed explicit sleeps between
tap and type.

**iOS UI tests are slow** — one took 134s. Worth keeping them out of the
fast feedback loop and running them on CI.

## Open issues / next steps

Phase 4 is complete. What remains is unchanged and mostly not mine:

1. **A real keystore** for release signing; the debug key is a placeholder.
2. **Confirm `versionCode`** against the actual store listing.
3. Serialization and the Vonage call path under R8 need a login to verify.
4. Everything in `open-concerns.md` still stands, store compliance first.
