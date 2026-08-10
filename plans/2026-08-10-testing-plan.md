# ASI 2.0 — Testing Plan

**Date:** 2026-08-10
**Applies to:** `kotlin` (Android) and `swift` (iOS)
**Companion:** [development plan](2026-08-10-development-plan.md)

CLAUDE.md mandates: **unit tests for every screen**, verification on the Android
Emulator / iOS Simulator / Claude Browser against `member-client`, and **test
reports saved as journal entries**. This plan makes those concrete.

---

## 1. Layers

| Layer | Scope | Runs |
|---|---|---|
| L1 Unit | View models, API mapping, formatters, token math | Every commit |
| L2 UI (component) | Each screen renders & reacts to state | Every commit |
| L3 Integration | Real dev backend: login → tiles → call setup | Per phase |
| L4 Device | Emulator + Simulator, real permissions, real video | Per phase |
| L5 Parity | Side-by-side vs `member-client` in Claude Browser | Per phase |

**Toolchain**
- Android: JUnit5 + MockK + Turbine (Flow), Compose UI tests, Robolectric,
  MockWebServer. `./gradlew test connectedAndroidTest`
- iOS: Swift Testing (or XCTest) + `URLProtocol` stubs, SwiftUI ViewInspector or
  snapshot tests. `xcodebuild test`

---

## 2. Design-system gates (automated, not eyeballed)

These are the tests that keep the palette honest. All derived from
[design/color-system.md](../design/color-system.md).

- **T-DS-1 Token contrast.** Assert computed WCAG ratios for every
  foreground/background pair the app actually uses, against the §5 table.
  Must include the three known traps as **negative** assertions:
  white-on-Justice-Gold (3.13), white-on-Active-Gold (2.22), Mid-Navy-on-Shield-Navy
  (1.49) — the test proves the app never forms these pairs.
- **T-DS-2 No raw hex.** Lint/test failing on any hex literal in UI code outside
  the token file.
- **T-DS-3 Palette allowlist.** Every colour in the token file is one of the 11
  approved hexes; no forbidden hex (`#FF4500`, `#7B2FBE`, `#00B4D8`, `#F0F0F0`)
  appears anywhere in either repo.
- **T-DS-4 CTA foreground.** Primary buttons use `ctaFg` (navy), never white.
- **T-DS-5 Dynamic type.** Screens render without clipping at the largest OS
  font setting.

## 3. Per-screen unit/UI tests

### Login
| ID | Case | Expected |
|---|---|---|
| T-L-1 | Valid credentials | Token stored, navigates to Home |
| T-L-2 | Invalid credentials | GraphQL `errors[]` surfaced as readable message |
| T-L-3 | `user` query fails | Login still succeeds; org falls back to `DEV_DEFAULTS` |
| T-L-4 | `casesByUser` fails | Login still succeeds; jurisdiction falls back |
| T-L-5 | Email whitespace | Trimmed before send |
| T-L-6 | Network offline | Readable error, no crash, retry available |
| T-L-7 | Password field | Masked; excluded from logs and crash reports |

### Home
| ID | Case | Expected |
|---|---|---|
| T-H-1 | Tiles load | Sorted by `sortOrder` |
| T-H-2 | Multilingual labels | English → org default → first → humanized `code` |
| T-H-3 | Type with no translations | Humanized `code` (e.g. `traffic_stop` → "Traffic Stop") |
| T-H-4 | Missing `iconFilePath` | Falls back to the code's icon, generic shield if unknown |
| T-H-5 | `partnerId` null | Chip row hidden entirely |
| T-H-6 | `partnerAttorneys` fails | Empty list, no error shown, auto-match only |
| T-H-7 | Attorney selected | Request carries `attorneyId`, **not** `queueId` |
| T-H-8 | Auto-match selected | Request carries `queueId`, **not** `attorneyId` |
| T-H-9 | Zero types configured | Empty-state message, no crash |
| T-H-10 | Greeting name | `displayName` first word → else email local-part, capitalized |
| T-H-11 | Loading | Skeletons, not a blank screen |

### Call — the phase machine
Cover all six phases of `starting | connecting | live | ended | no-attorney | error`.

| ID | Case | Expected |
|---|---|---|
| T-C-1 | Happy path | `starting → connecting → live` |
| T-C-2 | **`409` from `member-call`** | `no-attorney`, **retryable message, no crash** |
| T-C-3 | `500` | `error` with status surfaced |
| T-C-4 | Response missing `token`/`apiKey`/`sessionId` | `error`, never attempts connect |
| T-C-5 | Vonage connect error | `error`, message surfaced |
| T-C-6 | Publish error | `error` |
| T-C-7 | Remote hangs up (`connectionDestroyed`) | `ended` |
| T-C-8 | `sessionDisconnected` while live | `ended`; when not live, phase unchanged |
| T-C-9 | Member hangs up | Teardown; unpublish → destroy → disconnect, each guarded |
| T-C-10 | Leave screen mid-call | Full teardown, no leaked publisher/session |
| T-C-11 | Camera/mic denied | Clear explanation + settings route; no crash |
| T-C-12 | Location denied/unavailable/timeout | **Call proceeds without coords** |
| T-C-13 | Location granted | `memberLat`/`memberLng`(/`accuracy`) included |
| T-C-14 | Backgrounded during call | Documented, deliberate behaviour |
| T-C-15 | `ttlSeconds` | Sent as `3600` |

## 4. Integration (L3)

Against the dev backend, using `DEV_DEFAULTS` seed IDs:
- Real `login` → real token; authenticated GraphQL carries `Bearer`
- Unauthenticated `/query` is rejected as expected
- `member-call` returns all five credential fields
- `409` reproduced deliberately (no available attorney) and handled

## 5. Device verification (L4)

Per phase, both platforms:
1. Cold launch → login → home → place a call → connect → hang up
2. Deny camera, then mic, then location — verify each degradation
3. Airplane mode at each step
4. Rotation and largest font size on every screen
5. Screen reader pass: every control has a meaningful label

Simulator work uses the iOS Simulator tooling; Android uses the emulator.
Capture screenshots into the journal entry.

## 6. Parity vs `member-client` (L5)

Run the reference locally:

```bash
cd /Users/samsonphillip/attorney/ASI_2/member-client && npm install && npm run dev
```

Open it in Claude Browser beside the emulator/simulator and diff **behaviour**:
greeting text, tile order and labels, chip visibility, routing choice, each call
phase's copy, and the `409` message.

**Compare behaviour, not pixels.** `member-client` is intentionally off-palette
(blue/violet); a visual diff is expected and is *not* a defect. Colour is judged
against the PDF, never against the reference app.

`member-client` has no test runner in `package.json` and is read-only — we add no
tests there.

## 7. Definition of done (per screen)

- L1 + L2 tests green, including every relevant row above
- Design-system gates (§2) green
- Verified on emulator and simulator
- Parity checked against `member-client`
- Accessibility: labels, dynamic type, 4.5:1 text / 3:1 UI
- Journal entry with results, coverage notes, and screenshots

## 8. Coverage targets

| Area | Target |
|---|---|
| View models / state logic | ≥85% branch |
| API mapping + error paths | 100% of documented error branches |
| Call phase machine | 100% of the six phases |
| UI composables/views | Every screen has render + state tests |

Treat coverage as a floor, not a goal — T-C-2 (`409`) and T-C-12 (location
degradation) matter more than any percentage.

## 9. Reporting

One journal entry per test cycle at
`journals/YYYY-MM-DD-<task>-test-report.md`: what ran, pass/fail counts,
failures with root cause, coverage, screenshots, and open defects. Written as
work happens, not retrofitted.

## 10. Gaps this plan cannot yet close

- **Onboarding stages 3–5 are untestable** until the missing sign-up/payment/
  trial/guest endpoints are resolved (development plan §3, §9.1). No test IDs are
  assigned to them on purpose.
- **Token expiry has no defined correct behaviour** — no refresh operation exists
  (development plan §8). Tests will assert whatever we decide; the decision comes
  first.
- **Vonage native SDK behaviour is unproven** — the Phase 0 spike must land
  before Call tests can be trusted.
