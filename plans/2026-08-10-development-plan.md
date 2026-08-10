# ASI 2.0 — Development Plan

**Date:** 2026-08-10
**Scope:** Native Android (`kotlin`) and iOS (`swift`) member apps
**Status:** Draft for approval — no code written yet

---

## 1. Objective

Ship native Android and iOS member apps that match `member-client`'s behaviour
and API usage, rendered in the Attorney Shield visual system from the colour PDF
and the CodePen onboarding reference.

## 2. Reference authority

| Rank | Source | Governs |
|---|---|---|
| 1 | `design/color-system.md` (from the colour PDF) | All colour values |
| 2 | CodePen "Attorney - Shield App V6" | Layout, typography, screen inventory, flow |
| 3 | `member-client` | Behaviour, API contracts, state machines, errors |

Full rationale and the resolved PDF-vs-CodePen conflicts are in
[design/color-system.md](../design/color-system.md). Two rules that will
otherwise bite: **`member-client`'s blue/violet CSS is not the palette**, and
**never white text on gold** (3.13:1, fails WCAG AA).

---

## 3. Scope reality check — read this before estimating

The design board is **far larger than `member-client`**, and the API covers only
a fraction of it. Figures below are counted from the reference itself
([notes/design-reference-codepen.md](../notes/design-reference-codepen.md)), not
from its masthead.

**The CodePen board actually contains 66 phone frames** — 7 welcome-carousel
frames plus 59 numbered/annotated screens. Of the 66, **9 carry web browser
chrome** (`04`, `05`, `06`, `07`, `V1`, `T1`–`T4`) and **57 are native**.
Its masthead claim of "35 screens · 5 stages" is wrong on both counts: 35 is
merely the highest plain screen number, and only Stages **1, 4 and 5** exist —
there is no Stage 2 or Stage 3 header anywhere in the document.

**`member-client` implements 3 screens** — `LoginScreen` → `HomeScreen` →
`CallScreen`.

### Payment is on the web — this is the key structural finding

Plan choice, Stripe checkout and confirmation are **web pages on
`attorney-shield.com`**, not native screens. A deep link then hands the member
back to the app with their email pre-filled, and native registration resumes at
screen `08`. So payment always precedes phone verification.

```
native welcome (1-6) -> WEB 04 plan -> 05 Stripe -> 06 confirm -> 07 deep link
   -> native 08 phone -> 09 verify -> 10 details -> 11 address -> 12 PIN -> home
```

Those web frames sit inside the Stage 1 section and therefore **inherit a
"Native App" badge despite being browser frames** — a labelling bug in the
reference, not an instruction to build them natively. (A "Web" badge style is
defined in its stylesheet and never applied to anything.)

This materially reduces native scope: **we do not build checkout.** It also
means the real prices are **FreedomPlus `$16/mo`** and **FreedomFAMILY
`$38/mo`**, plus a `$0`-today 7-day trial — *not* the `$19`/`$179`/`$29` figures
on the colour PDF's marketing-site preview, which are a different surface.

### What is still blocked

Payment being on web does **not** clear the blockage — it moves it. Every
documented operation is:

- GraphQL `POST /query` — `login`, `user`, `casesByUser`,
  `adminIncidentTypeList` + `adminLanguageList`, `partnerAttorneys`
- REST `POST {API_BASE_URL}/api/vonage/video/member-call`

There is **no endpoint** behind any of the following native screens:

| Native feature | Screens | Endpoint |
|---|---|---|
| Phone entry + SMS/OTP verification | 08, 09 | none |
| Personal details, address | 10, 11 | none |
| 4-digit PIN set / verify / end session | 12, 34 | none |
| Document vault ("Digital Glovebox") | 14, 14A–14D, 31 | none |
| Situation preferences (pick 3) | 13B, 13C, 27B | none |
| Activity timeline | 32 | none |
| Plan / payment method / family sub-accounts | 33A, 33B, 33D | none |
| Notifications & nudge system | 15, 22–26 | none |
| Trial gate + in-app conversion | V2, T5–T8 | none |
| Guest session & feature gates | G1–G3 | none |

CLAUDE.md forbids inventing endpoints. Therefore:

> **Native registration (08–12) and the entire post-registration feature set are
> BLOCKED on backend work that does not exist yet.** They can be built as UI
> against mocks, but not as functioning features.

What *is* unblocked is the spine: welcome → login → home → connect → call.
That is Phases 0–2. Everything above is Phase 3+, and needs §9 answered first.

### What we can build today

| Capability | API support | Buildable now |
|---|---|---|
| Email/password login | `login` | ✅ |
| Member profile / org | `user` | ✅ |
| Case → jurisdiction/partner/case resolution | `casesByUser` | ✅ |
| Incident-type tiles (multilingual) | `adminIncidentTypeList` + `adminLanguageList` | ✅ |
| Attorney pre-selection | `partnerAttorneys` | ✅ |
| Place video call + Vonage credentials | `member-call` | ✅ |
| Welcome/onboarding carousel (7 frames) | none needed (static) | ✅ |
| Deep-link return from web checkout | none needed (client-side) | ✅ |
| Plan choice / checkout / confirmation | **not ours — web** | ➖ Out of native scope |
| Native registration 08–12, vault, family, nudges | **none** | ❌ Blocked (§3) |
| Trial gate, guest gate | **none** | ❌ Blocked (§3) |
| Token refresh | **none used** | ❌ See §8 |

---

## 4. Target architecture

Mirror structure across platforms so one review covers both.

```
<repo>/
  core/design/      tokens (colour, type, spacing), reusable components
  core/network/     GraphQL client, REST client, error mapping
  core/session/     auth + resolved member context, persistence
  feature/auth/     login
  feature/home/     greeting, attorney chips, incident tiles
  feature/call/     Vonage video, phase machine
```

### Android (`kotlin`)
- Jetpack Compose, Material 3 with a fully overridden colour scheme
- MVVM, `StateFlow` for state; Hilt for DI
- Ktor or OkHttp + `kotlinx.serialization`. **Raw `POST /query`**, not Apollo —
  faithfulness to `api.ts`'s hand-written queries matters more than codegen, and
  it avoids requiring a schema we do not have
- Vonage Video Android SDK
- `EncryptedSharedPreferences` for the session

### iOS (`swift`)
- SwiftUI, `@Observable` view models
- `URLSession` + `Codable`, same raw-GraphQL approach
- Vonage Video iOS SDK
- Keychain for the session

### Design system as code
Ship `design/color-system.md` §6 tokens as a single source file per platform
(`AsiColors.kt`, `AsiColors.swift`). **No raw hex literals in UI code** — this
is a lint/review gate, not a convention (§ testing plan).

---

## 5. Behaviour to port verbatim

From `member-client`. These are the details that make the app correct:

1. **Call routing** — send `attorneyId` when the member pre-selected one, **else**
   `queueId`. Never both.
2. **Call phase machine** — exactly `starting → connecting → live → ended`, plus
   `no-attorney` and `error` terminals.
3. **`409` on `member-call`** = `NoAttorneyError`, a *retryable* message. Never a
   crash, never a generic failure.
4. **Incident labels are multilingual** — English → org default language → first
   available → humanized `code`. Sort by `sortOrder`.
5. **Location is best-effort** — never block a call on geolocation. Resolve null
   on unsupported/denied/timeout.
6. **`listAttorneys` never throws** — empty list means auto-match/queue only, and
   the chip row hides entirely.
7. **Login never blocks on reference lookups** — `user` and `casesByUser` failures
   fall back to `DEV_DEFAULTS`.
8. **Validate video credentials** — reject a `member-call` response missing
   `apiKey`/`sessionId`/`token`/`callId`/`videoRoomId`.
9. **Publisher/session teardown** on unmount — unpublish, destroy, disconnect,
   each independently guarded.

## 6. Phases

Each phase ends with: unit tests green, emulator + simulator verified against
`member-client` in Claude Browser, and a journal entry.

**Phase 0 — Foundations** *(no product surface)*
Scaffold both projects with test harnesses. Encode design tokens and verify the
contrast table programmatically. Establish CI-runnable test commands.
*Exit:* `./gradlew test` and `xcodebuild test` both run green on a trivial test;
token contrast test passes.

**Phase 1 — Network + session**
GraphQL and REST clients, error mapping, session persistence, member-context
resolution with `DEV_DEFAULTS` fallback.
*Exit:* login against dev returns a token and resolves org/jurisdiction; unit
tests cover the fallback paths in §5.7.

**Phase 2 — Welcome → Login → Home → Call (the working spine)**
The three `member-client` screens in the Attorney Shield visual system, plus the
7-frame welcome carousel (static, no API needed) and the **deep-link return
handler** (Universal Links / App Links with email pre-fill and the "Open app
manually" fallback) — registration cannot continue without it.
*Exit:* a real video call connects on both platforms; all six call phases
reachable in tests; deep link resumes the app from a cold start; behaviour parity
checklist (§5) signed off.

**Phase 3 — Registration and member features** *(gated — see §3)*
Screens 08–12 and the post-registration set (vault, family, activity, nudges,
trial/guest gates). **Requires §9.1 and §9.2 answered first.** Built against
mocks only if we explicitly choose the mock path.

**Phase 4 — Hardening**
Accessibility audit, dynamic type, rotation, offline/airplane-mode, token
expiry, permission-denied paths, performance.

Phases 0–2 are the committed plan. Phase 3 is deliberately unestimated until §9
is answered.

## 7. Cross-cutting requirements

- **Accessibility:** WCAG AA (4.5:1 text / 3:1 UI) enforced by test, not review.
  Respect OS font scaling and screen readers; every icon-only control labelled.
- **Permissions:** camera and microphone are required for the call; location is
  optional and must degrade silently. Request at point of use with a clear
  rationale, and handle permanent denial.
- **Deep links** are a product requirement, not plumbing: iOS Universal Links and
  Android App Links from `attorney-shield.com`, resuming registration with the
  email pre-filled, plus the manual fallback. Must survive a cold start.
- **No secrets in the repo.** `apiKey` arrives per-call from the backend — never
  bundle Vonage credentials.
- **Config per environment**, mirroring `config.ts` (`GRAPHQL_URL`,
  `API_BASE_URL`, `DEV_DEFAULTS`, `CALL_TTL_SECONDS = 3600`).

## 8. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **App Store / Play compliance on web checkout.** The flow sells a digital subscription through web Stripe and deep-links back. Apple's rules on purchases for digital content and on steering users to external payment are the single most likely cause of a rejection here, and Google has parallel constraints | Could block release outright — not just delay it | **Settle the store strategy before Phase 3**, not at submission. The reference already anticipates part of this (33A carries App Store's required delete-account wording; no in-app plan changes). Needs a definitive answer on external-purchase entitlements vs in-app purchase |
| **Missing endpoints for native registration, vault, family, nudges, trial/guest gates** | Blocks everything past the call spine (§3) | Resolve §9.1 before Phase 3; Phases 0–2 are unaffected |
| **Deep-link return is load-bearing.** Registration cannot continue without it, and the reference plans to branch it by origin (app-initiated vs website-mobile) | A broken link strands members mid-signup, after payment | Treat as a Phase 2 deliverable with its own tests, not an afterthought. Universal Links + App Links, with the "Open app manually" fallback |
| **No token refresh exists** — `login` returns a `refreshToken` but `api.ts` never sends it; there is no refresh operation | Sessions die with no recovery path; native apps are backgrounded far longer than a web tab, so this hurts more than it does on web | Spike in Phase 1. Interim: detect auth failure and re-prompt login cleanly |
| **Web→native video SDK gap** — reference uses `@vonage/client-sdk-video`; native needs the Vonage Video Android/iOS SDKs | Could invalidate Phase 2 estimates | **De-risk in Phase 0** with a spike proving `apiKey`/`sessionId`/`token` connect natively |
| `member-call` has **no auth** today | Abuse surface | Flag to backend; do not design around it |
| CodePen is `v11` / "locked reference" but PDF conflicts with it | Rework | Authority order in §2; conflicts already resolved |
| `409` handling regressions | Members see a crash at the worst moment | Explicit test case, both platforms |
| Reference app not yet run locally | Parity checks can't start | Stand it up in Phase 0 (needs `serve-proxy.mjs`) |

## 9. Open questions — need answers before Phase 3

1. **Endpoints for native registration and the post-registration feature set —
   do they exist?** *Partially answered by the reference:* checkout is web, so
   payment is out of native scope. But screens 08–12 (phone, OTP, details,
   address, PIN) and the vault / family / activity / nudge / trial / guest
   features have no endpoints at all (§3). Is the intent that backend builds
   them, or that we ship UI against mocks? **Still the highest-value question.**
2. **App Store / Play strategy for a web-purchased subscription** — external
   purchase entitlement, or in-app purchase? This decides whether store review
   is on the critical path, and it is cheaper to answer now than at submission.
3. **Token refresh** — is there a refresh operation on the gateway we should use?
4. **Error/danger colour** — the palette forbids `#FF4500` and supplies no error
   colour. What should errors and hang-up use? (See colour-system §6.)
5. **Which CodePen palette values are stale** — confirm the PDF supersedes
   Deep Navy `#0A1626`, Live Green `#2E9E5B`, Trust Steel `#1A5FA8`.
6. **Family plan capacity is stated four different ways** in the reference —
   "covers up to 5" / "includes 3, add up to 2 more" / "You + 3" / "You + up to
   4" / "3 of 5 on your plan". Whether 5 includes the primary account is
   genuinely unresolved. **Must be settled before building the member stepper.**
7. **Frame geometry** — the board is drawn at 292×600 px but labelled
   "iPhone · 375pt". Confirm 375pt is the intent, in which case all reference
   measurements need rescaling ≈1.284×.
8. **Guest user type** — the reference says guests browse the real home and hit a
   gate on every member feature. Confirm nothing privileged is reachable.

## 10. Immediate next steps

1. Get §9.1 and §9.3 answered.
2. Phase 0: scaffold both repos, encode tokens, **run the Vonage native spike**.
3. Stand up `member-client` locally for parity comparison.
