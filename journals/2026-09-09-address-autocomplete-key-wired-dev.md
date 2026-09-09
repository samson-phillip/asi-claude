# 2026-09-09 — Address autocomplete: found a working key, wired for dev

Follow-on to `2026-09-08-address-autocomplete-phase1.md` (the feature was built
but dark). Samson added the **old app's repos** (`ANDROID/` = old Android app,
`attorneyShield/` = its signing keystores) and asked whether they held a Places key.

## The key

`ANDROID/app/google-services.json` (and `strings.xml`) commit a real Google API
key, and the old app's **`applicationId` is `com.app.attorney.shield` — the same
package as our new app**. The old app uses the Places **SDK** (`Places.initialize`),
which normally implies an Android-app-restricted key that the **web-service REST**
path I built would reject. So I ran **one** live test call (Samson-approved) to the
Places autocomplete web service with the key:

```
status: OK · predictions: 5
```

So the key **works with REST** — it is *not* app-restricted (a bare server call
with no app signature succeeded → it appears **application-unrestricted**). One key
serves both platforms' REST calls. Confirms the Cloud project + Places API + billing
are live.

## Wired for dev — key never committed

- **Android:** `app/build.gradle.kts` reads `MAPS_API_KEY` from `local.properties`
  (gitignored) / Gradle prop / env → `BuildConfig.PLACES_API_KEY` → passed to
  `AsiConfig.placesApiKey` at the one `AsiApi(AsiConfig.Dev.copy(...))` site.
  Verified: `BuildConfig.PLACES_API_KEY` populated, full `:app:testDebugUnitTest`
  green. `kotlin → dev 6bba820`.
- **iOS:** a gitignored `AttorneyShield/Secrets.plist` (auto-bundled via the
  synchronized folder group) read by `AsiConfig.bundledPlacesApiKey` → passed into
  the config at the one `AsiApi(config:)` site in `AttorneyShieldApp.init`.
  Verified: `xcodebuild build` **BUILD SUCCEEDED**, `Secrets.plist` bundles into the
  `.app`. `swift → dev f508ad1`.
- The key value lives ONLY in `kotlin/local.properties` and
  `swift/AttorneyShield/Secrets.plist` — both confirmed gitignored (`git check-ignore`).
  The committed changes are plumbing only.

## Before this ships in a RELEASE (not dev)

1. **Lock the key down** — it appears application-unrestricted (abuse/billing risk
   in a shipped client). At minimum restrict to the **Places API + quotas/alerts**;
   decide client-key vs backend-proxy with Innocent. A separate iOS-scoped key is
   cleaner. (Fine for dev.)
2. **Privacy governance** — App Store privacy labels / Play Data Safety for sending
   address text to Google (plan §6).

## Aside: SPM re-clone pain (self-inflicted)

Freeing disk earlier deleted `~/Library/Caches/org.swift.swiftpm`, forcing a full
SPM re-clone that kept failing on `stripe-ios` (`fetch-pack: invalid index-pack
output` / connection resets). Fixed with `git config --global http.version HTTP/1.1`
+ a larger `http.postBuffer`; the large clones then completed. Noted so the same
symptom is quick to fix next time.
