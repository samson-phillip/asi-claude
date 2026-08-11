# 2026-08-11 — Phase 1: networking and session

## Task
Port `member-client`'s API client and session state to both platforms: GraphQL
client, comms REST client, error mapping, session persistence, and the
best-effort member-context resolution. No UI — that is Phase 2.

## Repos and files touched

**`kotlin`** — `core/network/{AsiConfig,Models,AsiApi}.kt`,
`core/session/{MemberContext,SessionStore,SessionManager}.kt`,
tests `core/network/AsiApiTest.kt`, `core/session/SessionManagerTest.kt`.
Added OkHttp, kotlinx-serialization, coroutines, `androidx.security:security-crypto`,
MockWebServer.

**`swift`** — `Core/Network/{AsiConfig,Models,AsiApi}.swift`,
`Core/Session/{MemberContext,SessionStore,SessionManager}.swift`,
tests `AsiApiTests.swift`, `SessionManagerTests.swift`, `StubURLProtocol.swift`.
No new dependencies — URLSession and Security are enough.

**`asi-claude`** — this journal.

## What was ported

Every operation in `member-client/src/lib/api.ts`, verbatim in behaviour:
`login`, `user`, `casesByUser`, `adminIncidentTypeList` + `adminLanguageList`,
`partnerAttorneys`, and `POST /api/vonage/video/member-call`. Queries are the
reference's hand-written strings — there is no schema to generate from, and
faithfulness to the working client matters more than codegen.

The behaviours worth naming, because they are the ones easy to "tidy up" into
something worse:

- **Login never blocks on reference lookups.** `user` and `casesByUser` are both
  allowed to fail; the context falls back to `DEV_DEFAULTS`. Being locked out of
  the app because a reference query 500'd is a far worse outcome than a slightly
  wrong organization id.
- **`listAttorneys` never throws.** An empty roster means auto-match only. A
  roster lookup failing must not stop a member reaching an attorney.
- **Routing is exclusive**: `attorneyId` when pre-selected, **else** `queueId`,
  never both.
- **409 is a first-class outcome**, not an error case — a retryable message.
- **Credentials are validated before the SDK is touched**, so a missing token
  never becomes an opaque Vonage failure later.
- The case wins over the profile for `organizationId`; the profile is only the
  fallback.

## Decisions and why

**Storage is encrypted on both platforms.** The web client uses `localStorage`;
the native equivalent holds a bearer token on a device that can be lost, so
Android uses `EncryptedSharedPreferences` and iOS the Keychain with
`kSecAttrAccessibleAfterFirstUnlock` — the app may legitimately be launched
straight into a call after a reboot.

**Field names mirror the backend's inconsistency.** The gateway uses `userID` /
`organizationID`; the REST service uses `organizationId`. Mirroring that is
safer than tidying it, so the mapping stays checkable against `api.ts`.

**`AsiConfig.graphqlUrl` is a placeholder.** The reference only ever reaches the
gateway through a same-origin proxy, so the gateway's real host is not recorded
anywhere readable. It currently points at the comms host, which will fail loudly
rather than silently talk to the wrong service. **Needs the real URL before
Phase 2 can log in for real.**

## Problems hit (worth not rediscovering)

**Kotlin block comments nest.** `/api/*` inside a KDoc opened a nested comment
and silently swallowed the rest of the file; the reported error was
"unclosed comment" at the last line and a cascade of unresolved references. Any
`/*` sequence inside a doc comment does this.

**`org.json` is a stub in JVM unit tests.** Every `JSONObject` call throws
"not mocked". Request-body assertions use kotlinx-serialization instead.

**`assertThrows { runTest { … } }` hides the real exception** behind an
`IllegalStateException`. Replaced with a small inline helper — an inline lambda
can hold suspend calls when invoked from a suspend context.

**`androidx.security:security-crypto` 1.0.0 has `MasterKeys`, not
`MasterKey.Builder`** — the builder API only arrives in 1.1.0-alpha. Stayed on
the stable release and used its actual API.

**A latent duplicate type.** `NoAttorneyError`/`NoAttorneyException` had been
declared in the video layer during the Vonage spike and again in the network
layer. Swift caught it as a redeclaration; **Kotlin compiled it silently**
because the two were in different packages — so they were genuinely distinct
types and the call screen would have caught the wrong one. Now declared once, in
the network layer, next to the call that raises it.

**Swift Testing runs suites in parallel.** `StubURLProtocol` held process-wide
state, so `AsiApiTests` and `SessionManagerTests` stomped on each other's
response queues. Marking each suite `.serialized` does not help — that orders
tests *within* a suite. Diagnosed by running one suite alone (all green) versus
the whole target (many red). Fixed by keying stub state to a per-test handle
carried on a request header, which restores real isolation and keeps
parallelism.

## Test results

**Android — 61 unit tests, 0 failures** (`./gradlew :app:testDebugUnitTest`),
APK builds. Plus the 3 instrumented Vonage tests from the previous session.

| Suite | Tests |
|---|---|
| `AsiApiTest` | 28 |
| `SessionManagerTest` | 12 |
| `AsiContrastTest` | 17 |
| `PaletteAllowlistTest` | 4 |

**iOS — 67 tests, 0 failures** (`xcodebuild test`, iPhone 16 Pro).

| Suite | Tests |
|---|---|
| `AsiApiTests` | 28 |
| `SessionManagerTests` | 12 |
| `AsiContrastTests` | 18 |
| `PaletteAllowlistTests` | 4 |
| `VonageSdkSpikeTests` | 3 |
| `CallPhaseTests` | 2 |

The API and session suites are deliberately identical in count and intent across
platforms, so a behaviour drift on one shows up as a missing test on the other.

## API endpoints used
None live. All tests run against MockWebServer (Android) and a `URLProtocol`
stub (iOS).

## Open issues / next steps

1. **The GraphQL gateway URL is unknown** — see above. Blocks a real login.
2. **No token refresh still.** `login` returns a `refreshToken` nobody consumes.
   Captured in the model so it is not silently discarded; the decision about
   what to do on expiry is still open (development plan §8/§9.3).
3. **Phase 2 is next**: welcome carousel, Login, Home and Call screens wired to
   this layer, plus the deep-link handler.
4. Location is not implemented yet — it belongs with the Call screen, and must
   stay best-effort (never block a call).
5. Development plan §9 questions remain open; none block Phase 2's spine.
