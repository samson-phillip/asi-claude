# New Relic Mobile — what we need to integrate it

**To:** Innocent
**From:** Mobile team
**Re:** Integrating New Relic into the Attorney Shield apps

Happy to wire New Relic into both apps. It's the **New Relic Mobile** agent — a
native SDK, added separately to the Android (Kotlin) app and the iOS (Swift) app,
so a few of the items below are per-platform. Here's everything we need from your
side, what we'll handle, and one thing we should agree on before flipping it on.

---

## What we need from you / the New Relic side

1. **Two Mobile application tokens** — one for the **Android** app and one for the
   **iOS** app. In New Relic these come from *Add data → Mobile*, which creates a
   mobile app entity per platform and hands you a token. These are the only
   credentials the SDK needs at runtime, and they are **not** the account
   license/ingest key.

2. **The account region** — **US or EU** data centre. It changes the SDK's collector
   endpoint and init call, so we need this before wiring.

3. **A key for CI symbol uploads** (so crashes are human-readable):
   - **iOS** — a token/key to upload **dSYMs** (crash symbolication).
   - **Android** — the New Relic Gradle plugin uploads the **R8/ProGuard mapping**
     at build time; it needs network access + the app token.

4. **Which products you're enabling** — plain **Mobile APM** (crashes, network,
   ANRs, interaction traces) vs. also forwarding our **app logs** to New Relic
   Logs, vs. custom events/dashboards. That decides how much instrumentation we
   add beyond the baseline.

5. **A yes/no on the data-governance items** below.

---

## What we'll handle on the app side

- **Android** — add the New Relic Gradle plugin + agent dependency, add a small
  `Application` class (we don't have one today), and start the agent in
  `onCreate`. INTERNET permission is already in the manifest.
- **iOS** — add the agent via **Swift Package Manager** (we're already SPM-based),
  start it in the app's `init()`, and add a dSYM-upload build phase.
- **Network monitoring comes almost for free** — we use OkHttp (Android) and
  URLSession (iOS), both of which the agent auto-instruments, so request
  timing/errors appear without touching each call site.
- Wire the dSYM / mapping uploads into CI.
- Optionally add high-value custom events (trial conversion, call-connect,
  session-expired) once the baseline is in.

---

## One thing to agree on first — data governance ⚠️

This app handles **highly sensitive data**: legal representation during
law-enforcement encounters, PII, uploaded documents, and live attorney calls. By
default the Mobile agent auto-captures **request URLs, timings, device info, crash
context, and interaction traces**, all sent to a third-party vendor. Before
enabling it we should confirm:

- **PII / secret scrubbing** — bearer tokens, emails, user IDs and sensitive query
  params must not be captured as attributes. (The agents support URL/attribute
  redaction and disabling specific instrumentation — we'll configure this.)
- **Consent & jurisdiction** — GDPR/CCPA may require gating analytics behind
  user consent; we can start the agent only after opt-in, or run a reduced
  dataset.
- **Store disclosures** — enabling it means updating the **App Store privacy
  labels** and **Play Data Safety** form to declare diagnostics/performance
  collection.

None of these are technical blockers — just a deliberate call we should make
together given the domain, rather than defaulting it on.

---

## Effort

Once we have the tokens, region, and the governance decision: roughly **half a day
to a day per platform** for a clean baseline (SDK + init + CI symbol upload +
first-pass PII scrub), plus any custom events we choose to add.

---

## TL;DR — what we need back from you

- [ ] Android mobile app **token**
- [ ] iOS mobile app **token**
- [ ] Account **region** (US / EU)
- [ ] **CI upload key** for dSYMs / mapping files
- [ ] Which **products** to enable (Mobile APM only, or + Logs / custom events)
- [ ] Sign-off on the **data-governance** items (scrubbing, consent, store
      disclosures)

Send those over and we can have a baseline running behind a
disabled/consent flag, ready to switch on the moment it's approved.

Thanks,
Mobile team

---

## What Innocent sent back (2026-08-31)

**Dev-environment mobile application tokens** received for both platforms
(`member-ios-dev`, `member-android-dev`). These are the runtime SDK credential —
**not committed here.** They live out of band (build-time secret / password
manager); ask the token owner when wiring the SDK. Redacted so source control
never carries an ingest credential.

**Entity GUIDs** (identifiers, not credentials — used to link the mobile entity
directly, e.g. in dashboards / workloads):

- iOS — `ODQyMzU2MHxNT0JJTEV8QVBQTElDQVRJT058MTU4OTI3MTA3MA`
- Android — `ODQyMzU2MHxNT0JJTEV8QVBQTElDQVRJT058MTU4OTI3MTA2OQ`

Reference artifact from Innocent:
<https://claude.ai/code/artifact/5bab0f10-f2eb-47a6-a78d-a617dfc17a8c>

### Still outstanding

- [ ] **Region** (US / EU) — still needed; it sets the collector endpoint + init
      call. (The `-NRMA` token suffix implies a standard US account, but confirm.)
- [ ] **CI upload key** for dSYMs (iOS) / R8 mapping (Android).
- [ ] **Products** to enable (Mobile APM only vs. + Logs / custom events).
- [ ] **Data-governance sign-off** (PII scrubbing, consent, store disclosures).
- [ ] **UAT + prod tokens** — Innocent said he'll provide these later. These are
      **dev** tokens only; do not ship them to a release build.

> ⚠️ **These are credentials.** They are the low-sensitivity app-side ingest kind
> (they end up embedded in the shipped binary anyway), but they can still be used
> to write data into our New Relic account. Prefer injecting them at **build time**
> (CI secret / xcconfig / `local.properties`) over hardcoding, and keep prod/UAT
> tokens out of source control entirely. Recorded here as dev-only reference until
> the integration lands.
