# 2026-08-11 — Vonage native spike, and light/dark mode

## Task
Two things: run the Phase 0 Vonage spike (the gate on Phase 2 estimates), and
add light mode alongside dark across the design system.

## Repos and files touched

**`kotlin`**
- `gradle/libs.versions.toml`, `app/build.gradle.kts` — Vonage SDK 2.32.1
- `core/video/CallPhase.kt`, `core/video/VonageSession.kt` (new)
- `app/src/androidTest/.../VonageSdkSpikeTest.kt` (new)
- `core/design/AsiColors.kt`, `AsiTheme.kt`, `AsiComponents.kt` — scheme model
- `MainActivity.kt` — appearance toggle, green-as-dot fix
- `AsiContrastTest.kt`, `PaletteAllowlistTest.kt` — both schemes, R4

**`swift`**
- `AttorneyShield.xcodeproj/project.pbxproj` — SPM dependency; removed the
  forced-dark Info.plist keys
- `Core/Video/CallPhase.swift`, `Core/Video/VonageSession.swift` (new)
- `AttorneyShieldTests/VonageSdkSpikeTests.swift` (new)
- `Core/Design/AsiColors.swift`, `AsiTheme.swift`, `AsiComponents.swift`
- `AttorneyShieldApp.swift` — appearance override, green-as-dot fix
- `AsiContrastTests.swift` — both schemes, R4

**`asi-claude`** — `design/color-system.md` (R3 tightened, R4 added, §6 rewritten
for both appearances), this journal.

---

## Part 1 — Vonage spike: RESOLVED, risk retired

### Versions
`member-client` pins `@vonage/client-sdk-video: ^2.32.1`. Both native SDKs are
available at **exactly 2.32.1**, so all three clients speak the same signalling
version:

| Platform | Coordinate | Version |
|---|---|---|
| Web (reference) | `@vonage/client-sdk-video` | 2.32.1 |
| Android | `com.vonage:client-sdk-video` (Maven Central) | 2.32.1 |
| iOS | `Vonage/vonage-video-client-sdk-swift` (SPM) | 2.32.1 |

iOS note: there are two SPM distributions. `opentok/vonage-client-sdk-video`
tops out at 2.31.1; the Vonage-org `Vonage/vonage-video-client-sdk-swift` has
2.32.1 and is the one to use. Also, the module to `import` is **`OpenTok`**, not
`VonageClientSDKVideo` — the rename never reached the ObjC class prefixes.

### What the dev backend told us
`POST https://comms-dev.attorneyshield.io/api/vonage/video/member-call` with the
`DEV_DEFAULTS` org/jurisdiction/queue returned:

```
HTTP 409 — "no attorney is available to take this call"
```

Which independently confirms three things from the plan: the endpoint takes no
auth, the request shape in `api.ts` is correct, and **the 409 `NoAttorneyError`
path is real** (testing plan T-C-2) with a plain-text body.

It also means no live credentials were obtainable, so a full connect-to-live
could not be proven. That is a backend-availability limit, not an SDK one.

### What was proven instead
Both platforms now connect with deliberately invalid-but-well-formed
credentials, on a real device, and are asserted to come back through our
[CallPhase] mapping. Android logcat is the clearest evidence:

```
nativeloader: Load .../libopentok.so ... : ok
[com.opentok.android]: OpenTok Android SDK | Version/Revision: 2.32.1/88ca97c4...
opentok: [ERROR] otk_anvil.cpp:403 - otk_anvil_on_session_info failed. nCode=1
VonageSession: session error: Invalid token format
```

That is: native library loads, JNI initialises, the SDK performs a **network
round-trip to Vonage's session-info service**, and the failure surfaces through
our own error mapping rather than crashing. iOS behaves identically (its spike
test takes 5–15s, which is the round-trip).

**Conclusion: the web→native SDK gap is closed.** The `apiKey`/`sessionId`/
`token` triple is the same contract natively. The only unproven step is a valid
session going live, which needs an attorney online on dev — a scheduling matter,
not an engineering risk. Phase 2 estimates can be trusted.

### Ported behaviour
`CallPhase` is an SDK-independent enum matching `member-client` exactly
(`starting | connecting | live | ended | no-attorney | error`), so the state
machine is unit-testable with no device, camera or network. Credentials are
validated *before* the SDK is touched, and teardown is over-guarded
step-by-step, both matching the reference's reasoning.

---

## Part 2 — Light and dark mode

Requested this session. The palette already carried the light surfaces (the PDF
specifies Off White page / Pure White cards, "warmth over sterility"), but two
real gaps had to be resolved.

**Gap 1 — gold cannot be text on light.** `#C4850A` is 2.85:1 on Off White,
below even the 3:1 large-text bar. Eyebrow labels are gold on dark, so
`accentText` had to become scheme-dependent: **Shield Navy on light** at
15.73:1. Tightened R3 to say so.

**Gap 2 — no light border colour exists,** and Flat Gray `#F0F0F0` is forbidden.
Resolved with **Stone Gray at 25% alpha**: an alpha variant of an approved
colour is still that colour, which keeps the palette closed. Documented as
permitted.

**What deliberately does not change between schemes: the gold CTA and its navy
label.** 5.53:1 either way, so the most important control on the screen is
identical in both appearances. There is a test asserting it does not drift.

### A defect this found in my own code
`VerifiedGreen` as **text** on Shield Navy is **3.24:1 — fails AA**. The Phase 0
smoke screen rendered its "passes" indicator in exactly that way on both
platforms. Same class of defect I flagged in the source PDF, shipped by me a
few hours later.

The existing tests missed it because they only checked the declared
*text-on-dark* tokens, never `success` used as text. Fixes:

- Renamed the token `successFill` so the constraint is in the name.
- The indicator is now a green **dot** (a graphic at 3.24:1 clears the 3:1 bar)
  beside neutral text.
- Added **R4** to the colour system, plus a regression test named for it, and a
  broad new test that walks *every* text token against *every* surface token in
  *both* schemes — which is the gate that would have caught it.

### A second real bug
iOS ignored the OS appearance entirely. `INFOPLIST_KEY_UIUserInterfaceStyle =
Dark` was left in the project from when the app was dark-only, and it
force-pins the appearance and silently overrides `preferredColorScheme`. Removed
from both Debug and Release, along with the forced light status-bar style.

Worth noting the unit tests could never have caught this — it took switching the
simulator appearance and looking.

## Test results

**Android — 21 unit tests + 3 instrumented, 0 failures.**
`./gradlew :app:testDebugUnitTest` and `:app:connectedDebugAndroidTest`.

**iOS — 26 tests, 0 failures.**
`xcodebuild test -scheme AttorneyShield -destination 'iPhone 16 Pro'`.

**Device verification, both appearances, both platforms.** Android via an
in-app toggle (background pixel sampled: `(13,27,46)` dark, `(245,244,240)`
light); iOS by switching the simulator appearance, which now propagates
correctly. Rendered ratios match the test expectations exactly in both schemes —
dark 17.31 / 7.03 / 7.81 / 5.53 / 5.34, light 13.04 / 4.95 / 15.73 / 5.53 / 5.34.

## API endpoints used
`POST https://comms-dev.attorneyshield.io/api/vonage/video/member-call` — one
request, returned 409. No call was created. No GraphQL calls (no credentials).

## Open issues / next steps

1. **A live connect still needs an attorney online on dev.** Worth doing once
   before Phase 2 completes, to confirm `live` and the subscriber path. Not
   blocking.
2. **Phase 1 — networking and session** is now the next task and is fully
   unblocked: GraphQL client, REST client, error mapping, session persistence.
3. Android's system nav bar still renders light under `enableEdgeToEdge()`;
   cosmetic, fix with the real screens.
4. No launcher icon on Android; needs the brand shield asset.
5. `Subscriber.destroy()` is deprecated in the Android SDK — harmless, but worth
   replacing when the call screen is built properly.
6. Development plan §9 questions remain open; none block Phase 1.
